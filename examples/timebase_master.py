#!/usr/bin/env python3
#
#  timebase_master.py
#
"""A simple JACK timebase master."""

import argparse
import sys
from threading import Event

import jack


class TimebaseMasterClient(jack.Client):
    def __init__(self, name, *, bpm=120.0, beats_per_bar=4, beat_type=4,
                 ticks_per_beat=1920, conditional=False, debug=False, **kw):
        super().__init__(name, **kw)
        self.beats_per_bar = int(beats_per_bar)
        self.beat_type = int(beat_type)
        self.bpm = bpm
        self.conditional = conditional
        self.debug = debug
        self.ticks_per_beat = int(ticks_per_beat)
        self.stop_event = Event()
        self.set_shutdown_callback(self.shutdown)

    def shutdown(self, status, reason):
        print('JACK shutdown:', reason, status)
        self.stop_event.set()

    def _tb_callback(self, state, nframes, pos, new_pos):
        if self.debug and new_pos:
            print("New pos:", jack.position2dict(pos))

        # Adapted from:
        # https://github.com/jackaudio/jack2/blob/develop/example-clients/transport.c#L66
        if new_pos:
            pos.beats_per_bar = float(self.beats_per_bar)
            pos.beats_per_minute = self.bpm
            pos.beat_type = float(self.beat_type)
            pos.ticks_per_beat = float(self.ticks_per_beat)
            pos.valid |= jack._lib.JackPositionBBT

            minutes = pos.frame / (pos.frame_rate * 60.0)
            abs_tick = minutes * self.bpm * self.ticks_per_beat
            abs_beat = abs_tick / self.ticks_per_beat

            pos.bar = int(abs_beat / self.beats_per_bar)
            pos.beat = int(abs_beat - (pos.bar * self.beats_per_bar) + 1)
            pos.tick = int(abs_tick - (abs_beat * self.ticks_per_beat))
            pos.bar_start_tick = pos.bar * self.beats_per_bar * self.ticks_per_beat
            pos.bar += 1  # adjust start to bar 1
        else:
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
                        print("Pos:", jack.position2dict(pos))

    def become_timebase_master(self, conditional=None):
        return self.set_timebase_callback(self._tb_callback, conditional
                                          if conditional is not None
                                          else self.conditional)


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        '-d', '--debug',
        action='store_true',
        help="Enable debug messages")
    ap.add_argument(
        '-c', '--conditional',
        action='store_true',
        help="Exit if another timebase master is already active")
    ap.add_argument(
        '-n', '--client-name',
        metavar='NAME',
        default='timebase',
        help="JACK client name (default: %(default)s)")
    ap.add_argument(
        '-m', '--meter',
        default='4/4',
        help="Meter as <beats-per-bar>/<beat-type> (default: %(default)s)")
    ap.add_argument(
        '-t', '--ticks-per-beat',
        type=int,
        metavar='NUM',
        default=1920,
        help="Ticks per beat (default: %(default)s)")
    ap.add_argument(
        'tempo',
        nargs='?',
        type=float,
        default=120.0,
        help="Tempo in beats per minute (0.1-300.0, default: %(default)s)")

    args = ap.parse_args(args)

    try:
        beats_per_bar, beat_type = (int(x) for x in args.meter.split('/', 1))
    except (TypeError, ValueError):
        print("Error: invalid meter: {}\n".format(args.meter))
        ap.print_help()
        return 2

    try:
        tbmaster = TimebaseMasterClient(
            args.client_name,
            bpm=max(0.1, min(300.0, args.tempo)),
            beats_per_bar=beats_per_bar,
            beat_type=beat_type,
            ticks_per_beat=args.ticks_per_beat,
            debug=args.debug)
    except jack.JackError as exc:
        return "Could not create timebase master JACK client: {}".format(exc)

    with tbmaster:
        if tbmaster.become_timebase_master(args.conditional):
            try:
                print("Press Ctrl-C to quit...")
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
            return "Timebase master already present. Exiting..."


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
