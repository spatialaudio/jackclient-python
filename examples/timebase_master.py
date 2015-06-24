#!/usr/bin/env python3

"""JACK client that set timebase master.

Usage : timebase_master.py [<BPM> [<beats per bar> [<ticks per beat>]]]

This Client will register itself as `timebase master` and set extended
position information :

    * BPM
    * Bar, Beat and Tick according to current position
    * beat per bar, ticks per beat
    * beat type, bar start tick

"""
import jack
import sys

argv = iter(sys.argv)
next(argv)  # skip script name

BPM = next(argv, 130)
BAR_START_TICK = 0.0
BEATS_PER_BAR = float(next(argv, 4.0))
BEAT_TYPE = 4.0
TICKS_PER_BEAT = float(next(argv, 960.0))

client = jack.Client("Timebase Master")

print("BPM: %s" % BPM)
print("Beats per bar : %s" % BEATS_PER_BAR)
print("Ticks per beat: %s" % TICKS_PER_BEAT)


@client.set_timebase_callback
def timebase_callback(state, blocksize, pos, new_pos):

    if new_pos:
        print("Position changed")

    if not pos.frame_rate:
        print("Frame position : %s" % pos.frame)
        print("Frame rate : %s" % pos.frame_rate)
        print("State : %s" % state)
        print("Valid : %s" % pos.valid)

    if pos.valid & 0x10:
        check_modified_fields(pos)

    # Set static fields (bpm, beat per bar, ...)
    pos.bar_start_tick = BAR_START_TICK
    pos.beats_per_bar = BEATS_PER_BAR
    pos.beat_type = BEAT_TYPE
    pos.ticks_per_beat = TICKS_PER_BEAT
    pos.beats_per_minute = BPM

    # Compute and set variable fields (bar, beat, ticks)
    ticks_per_second = ((pos.beats_per_minute *
                         pos.ticks_per_beat) / 60)
    ticks = (ticks_per_second * pos.frame) / pos.frame_rate
    (beats, pos.tick) = divmod(int(round(ticks, 0)),
                               int(round(pos.ticks_per_beat, 0)))
    (bar, beat) = divmod(beats, int(round(pos.beats_per_bar, 0)))
    pos.bar = bar + 1
    pos.beat = beat + 1

    # Set valids fields
    pos.valid = 0x10  # BBT Fields

    return None


def check_modified_fields(pos):
    print("Checking fields...")
    modified = False
    if pos.bar_start_tick != BAR_START_TICK:
        modified = True
        print("'bar start tick' modified %s -> %s"
              % (BAR_START_TICK, pos.bar_start_tick))
    if pos.beats_per_bar != BEATS_PER_BAR:
        modified = True
        print("'beats per bar' modified %s -> %s"
              % (BEATS_PER_BAR, pos.beats_per_bar))
    if pos.beat_type != BEAT_TYPE:
        modified = True
        print("'beat type' modified b%s -> %s"
              % (BEAT_TYPE, pos.beat_type))
    if pos.ticks_per_beat != TICKS_PER_BEAT:
        modified = True
        print("'ticks per beat' modified %s -> %s"
              % (TICKS_PER_BEAT, pos.ticks_per_beat))
    if pos.beats_per_minute != BPM:
        modified = True
        print("'beats per minute' modified %s -> %s"
              % (BPM, pos.beats_per_minute))
    if modified:
        print("pos.valid : %s" % pos.valid)


# activate client
with client:

    response = BPM
    while response != '':
        BPM = int(response)
        print("#" * 80)
        print(("enter new BPM and press Return "
               "or press Return to quit"))
        print("#" * 80)
        response = input()
