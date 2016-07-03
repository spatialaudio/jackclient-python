#!/usr/bin/env python3

"""
Create a JACK client that plays a soundfile to all outputs (loudspeakers and headphones).
"""

import sys
import signal
import os
import jack
import threading
import numpy as np
import soundfile as sf

data, fs = sf.read('tschirp.wav')


if sys.version_info < (3, 0):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # See other examples
else:
    # If you use Python 3.x, everything is fine.
    pass

client = jack.Client("allOutputClient")

out1 = client.outports.register("output_1")
out2 = client.outports.register("output_2")
out3 = client.outports.register("output_3")
out4 = client.outports.register("output_4")


@client.set_process_callback
def process(frames):
    assert len(client.inports) == len(client.outports)
    assert frames == client.blocksize
    out1.get_arrey()[:] = block1 # np.array(client.blocksize, dtype=np.float32)
    out2.get_arrey()[:] = block2
    out3.get_arrey()[:] = block1
    out4.get_arrey()[:] = block2

@client.set_samplerate_callback
def samplerate(samplerate):
    global fs
    fs = samplerate


with client:
    # Note the confusing (but necessary) orientation of the 
    # driver backend ports: playback ports are "input" to 
    # the backend, and capture ports are "output" from it.
    playback = client.get_ports(is_physical=True, is_input=True)
    if not capture:
        raise RuntimeError("No physical capture ports")

    for src, dest in zip(client.outports, playback):
        client.connect(src, dest)

    try:
        event.wait()
    except KeyboardInterrupt:
        print("\nInterrupted by user")

