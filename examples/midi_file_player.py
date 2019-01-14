#!/usr/bin/env python3
"""Play a MIDI file.

This uses the "mido" module for handling MIDI: https://mido.readthedocs.io/

Pass the MIDI file name as first command line argument.

If a MIDI port name is passed as second argument, a connection is made.

"""
import sys
import threading

import jack
from mido import MidiFile

argv = iter(sys.argv)
next(argv)
filename = next(argv, '')
connect_to = next(argv, '')
if not filename:
    sys.exit('Please specify a MIDI file')
try:
    mid = iter(MidiFile(filename))
except Exception as e:
    sys.exit(type(e).__name__ + ' while loading MIDI: ' + str(e))

client = jack.Client('MIDI-File-Player')
port = client.midi_outports.register('output')
event = threading.Event()
msg = next(mid)
fs = None  # sampling rate
offset = 0


@client.set_process_callback
def process(frames):
    global offset
    global msg
    port.clear_buffer()
    while True:
        if offset >= frames:
            offset -= frames
            return  # We'll take care of this in the next block ...
        # Note: This may raise an exception:
        port.write_midi_event(offset, msg.bytes())
        try:
            msg = next(mid)
        except StopIteration:
            event.set()
            raise jack.CallbackExit
        offset += round(msg.time * fs)


@client.set_samplerate_callback
def samplerate(samplerate):
    global fs
    fs = samplerate


@client.set_shutdown_callback
def shutdown(status, reason):
    print('JACK shutdown:', reason, status)
    event.set()


with client:
    if connect_to:
        port.connect(connect_to)
    print('Playing', repr(filename), '... press Ctrl+C to stop')
    try:
        event.wait()
    except KeyboardInterrupt:
        print('\nInterrupted by user')
