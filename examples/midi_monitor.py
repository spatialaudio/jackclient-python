#!/usr/bin/env python3

"""JACK client that prints all received MIDI events."""

import jack
import binascii

client = jack.Client("MIDI-Monitor")
port = client.midi_inports.register("input")


def callback(frames, userdata):
    for offset, data in port.incoming_midi_events():
        # TODO: use ringbuffer
        print(client.last_frame_time + offset, binascii.hexlify(data))
    return jack.CALL_AGAIN

client.set_process_callback(callback)
client.activate()

print("#" * 80)
print("press Return to quit")
print("#" * 80)
input()
client.close()
