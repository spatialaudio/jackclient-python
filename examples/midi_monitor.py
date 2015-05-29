#!/usr/bin/env python3

"""JACK client that prints all received MIDI events."""

import jack
import binascii

client = jack.Client("MIDI-Monitor")
port = client.midi_inports.register("input")


@client.set_process_callback
def process(frames):
    for offset, data in port.incoming_midi_events():
        print("{0}: 0x{1}".format(client.last_frame_time + offset,
                                  binascii.hexlify(data).decode()))

with client:
    print("#" * 80)
    print("press Return to quit")
    print("#" * 80)
    input()
