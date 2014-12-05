#!/usr/bin/env python3

"""Create a JACK client that copies input audio directly to the outputs.

This is somewhat modeled after the "thru_client.c" example of JACK 2:
http://github.com/jackaudio/jack2/blob/master/example-clients/thru_client.c

If you have a microphone and loudspeakers connected, this might cause an
acoustical feedback!

"""

import jack
import threading
import sys
import signal

# TODO: 1st argument: client name
# TODO: default client name: basename of argv[0]
# TODO: 2nd argument: server name (default None)

client = jack.Client("Through-Client")

# TODO: check for status: JackServerStarted and JackNameNotUnique

event = threading.Event()


def process(frames, userdata):
    assert len(client.inports) == len(client.outports)
    assert frames == client.blocksize
    for i, o in zip(client.inports, client.outports):
        o.get_buffer()[:] = i.get_buffer()
    return jack.CALL_AGAIN

client.set_process_callback(process)


def shutdown(status, reason, userdata):
    print("JACK shutdown!")
    print("status:", jack.decode_status(status))
    print("reason:", reason)
    event.set()

client.set_shutdown_callback(shutdown)

# create two port pairs
for number in range(1, 3):
    client.inports.register("input_{0}".format(number))
    client.outports.register("output_{0}".format(number))

# Tell the JACK server that we are ready to roll.
# Our process() callback will start running now.
client.activate()

# Connect the ports.  You can't do this before the client is activated,
# because we can't make connections to clients that aren't running.
# Note the confusing (but necessary) orientation of the driver backend
# ports: playback ports are "input" to the backend, and capture ports
# are "output" from it.

capture = client.get_ports(is_physical=True, is_output=True)
if not capture:
    raise RuntimeError("No physical capture ports")

for src, dest in zip(capture, client.inports):
    client.connect(src, dest)

playback = client.get_ports(is_physical=True, is_input=True)
if not playback:
    raise RuntimeError("No physical playback ports")

for src, dest in zip(client.outports, playback):
    client.connect(src, dest)

if sys.version_info < (3, 0):
    # In Python 2.x, event.wait() cannot be interrupted with Ctrl+C.
    # Therefore, we disable the whole KeyboardInterrupt mechanism.
    # This will not close the JACK client properly, but at least we can
    # use Ctrl+C.
    signal.signal(signal.SIGINT, signal.SIG_DFL)
else:
    # If you use Python 3.x, everything is fine.
    pass

try:
    print("Press Ctrl+C to stop")
    event.wait()
except KeyboardInterrupt:
    print("\nInterrupted by user")

client.close()
