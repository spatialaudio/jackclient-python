#!/usr/bin/env python3

"""JACK client that set timebase master.

This Client will register itself as `timebase master` and set extended
position information :

    * BPM
    * Bar, Beat and Tick according to current position
    * beat per bar, ticks per beat
    * beat type, bar start tick

"""
import jack

BPM = 130
BAR_START_TICK = 0.0
BEATS_PER_BAR = 4.0
BEAT_TYPE = 4.0
TICKS_PER_BEAT = 960.0


def frames2ticks(frame, ticks_per_beat, beats_per_minute, frame_rate):
    ticks_per_second = (beats_per_minute * ticks_per_beat) / 60
    return (ticks_per_second * frame) / frame_rate


client = jack.Client("Timebase Master")


@client.set_timebase_callback
def timebase_callback(state, nframes, pos, new_pos):
    pos.valid = 0x10  # BBT Fields
    pos.bar_start_tick = BAR_START_TICK
    pos.beats_per_bar = BEATS_PER_BAR
    pos.beat_type = BEAT_TYPE
    pos.ticks_per_beat = TICKS_PER_BEAT
    pos.beats_per_minute = BPM
    ticks = frames2ticks(pos.frame,
                         pos.ticks_per_beat,
                         pos.beats_per_minute,
                         pos.frame_rate)
    (beats, pos.tick) = divmod(int(round(ticks, 0)),
                               int(round(pos.ticks_per_beat, 0)))
    (bar, beat) = divmod(beats, int(round(pos.beats_per_bar, 0)))
    pos.bar = bar + 1
    pos.beat = beat + 1
    return None


# activate !
with client:
    print("#" * 80)
    print("press Return to quit")
    print("#" * 80)
    input()
