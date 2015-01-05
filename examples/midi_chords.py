#!/usr/bin/env python3

"""JACK client that creates minor triads from single MIDI notes.

All MIDI events are passed through.
Two additional events are created for each NoteOn and NoteOff event.

"""
import jack
import struct

NOTEON = 0x90
NOTEOFF = 0x80

INTERVALS = 3, 7  # minor triad

client = jack.Client("MIDI-Chord-Generator")
inport = client.midi_inports.register("input")
outport = client.midi_outports.register("output")


def callback(frames, userdata):
    outport.clear_buffer()
    for offset, indata in inport.incoming_midi_events():
        outdata = outport.reserve_midi_event(offset, len(indata))
        # Note: potential errors are ignored! If len(outdata) == 0 -> error
        outdata[:] = indata
        if len(indata) == 3:
            cmd, pitch, vel = struct.unpack('3B', indata)
            if cmd in (NOTEON, NOTEOFF):
                for i in INTERVALS:
                    outport.write_midi_event(offset, (cmd, pitch + i, vel))
                    # An exception will be raised if MIDI buffer is full
    return jack.CALL_AGAIN

client.set_process_callback(callback)
client.activate()

print("#" * 80)
print("press Return to quit")
print("#" * 80)
input()
client.close()
