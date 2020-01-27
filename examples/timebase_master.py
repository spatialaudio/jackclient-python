#!/usr/bin/env python3
"""A simple JACK timebase master."""
import argparse
from threading import Event

import jack


class TimebaseMasterClient(jack.Client):
    def __init__(self, name, *, bpm=120.0, beats_per_bar=4, beat_type=4,
                 ticks_per_beat=1920, conditional=False, debug=False, **kw):
        super().__init__(name, **kw)
        self.beats_per_bar = beats_per_bar
        self.beat_type = beat_type
        self.bpm = bpm
        self.conditional = conditional
        self.debug = debug
        self.ticks_per_beat = ticks_per_beat
        self.stop_event = Event()
        self.set_shutdown_callback(self.shutdown_callback)

    def shutdown_callback(self, status, reason):
        print('JACK shutdown:', reason, status)
        self.stop_event.set()

    def timebase_callback(self, state, nframes, pos, new_pos):
        if self.debug and new_pos:
            print('New pos:', jack.position2dict(pos))

        # Adapted from:
        # https://github.com/jackaudio/jack2/blob/develop/example-clients/transport.c#L66
        if new_pos:
            pos.beats_per_bar = self.beats_per_bar
            pos.beats_per_minute = self.bpm
            pos.beat_type = self.beat_type
            pos.ticks_per_beat = self.ticks_per_beat
            pos.valid = jack.POSITION_BBT

            minutes = pos.frame / (pos.frame_rate * 60.0)
            abs_tick = minutes * self.bpm * self.ticks_per_beat
            abs_beat = abs_tick / self.ticks_per_beat

            pos.bar = int(abs_beat / self.beats_per_bar)
            pos.beat = int(abs_beat - (pos.bar * self.beats_per_bar) + 1)
            pos.tick = int(abs_tick - (abs_beat * self.ticks_per_beat))
            pos.bar_start_tick = (
                pos.bar * self.beats_per_bar * self.ticks_per_beat)
            pos.bar += 1  # adjust start to bar 1
        else:
            assert pos.valid & jack.POSITION_BBT
            # Compute BBT info based on previous period.
            pos.tick += int(nframes * pos.ticks_per_beat *
                            pos.beats_per_minute / (pos.frame_rate * 60))

            while pos.tick >= pos.ticks_per_beat:
                pos.tick -= int(pos.ticks_per_beat)
                pos.beat += 1

                if pos.beat > pos.beats_per_bar:
                    pos.beat = 1
                    pos.bar += 1
                    pos.bar_start_tick += pos.beats_per_bar * pos.ticks_per_beat

                    if self.debug:
                        print('Pos:', jack.position2dict(pos))

    def become_timebase_master(self, conditional=None):
        if conditional is None:
            conditiona = self.conditional
        return self.set_timebase_callback(self.timebase_callback, conditional)


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        '-d', '--debug',
        action='store_true',
        help='enable debug messages')
    ap.add_argument(
        '-c', '--conditional',
        action='store_true',
        help='exit if another timebase master is already active')
    ap.add_argument(
        '-n', '--client-name',
        metavar='NAME',
        default='timebase',
        help='JACK client name (default: %(default)s)')
    ap.add_argument(
        '-m', '--meter',
        default='4/4',
        help='meter as <beats-per-bar>/<beat-type> (default: %(default)s)')
    ap.add_argument(
        '-t', '--ticks-per-beat',
        type=int,
        metavar='NUM',
        default=1920,
        help='ticks per beat (default: %(default)s)')
    ap.add_argument(
        'tempo',
        nargs='?',
        type=float,
        default=120.0,
        help='tempo in beats per minute (default: %(default)s)')

    args = ap.parse_args(args)

    try:
        beats_per_bar, beat_type = map(float, args.meter.split('/'))
    except ValueError:
        ap.error('Invalid meter: ' + args.meter)

    try:
        tbmaster = TimebaseMasterClient(
            args.client_name,
            bpm=args.tempo,
            beats_per_bar=beats_per_bar,
            beat_type=beat_type,
            ticks_per_beat=args.ticks_per_beat,
            debug=args.debug)
    except jack.JackError as exc:
        ap.exit('Could not create timebase master JACK client: {}'.format(exc))

    with tbmaster:
        if tbmaster.become_timebase_master(args.conditional):
            try:
                print('Press Ctrl-C to quit...')
                tbmaster.stop_event.wait()
            except KeyboardInterrupt:
                print('')
            finally:
                try:
                    tbmaster.release_timebase()
                except jack.JackError:
                    # another JACK client might have grabbed timebase master
                    pass
        else:
            ap.exit('Timebase master already present. Exiting...')


if __name__ == '__main__':
    main()
