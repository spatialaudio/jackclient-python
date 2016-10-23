#!/usr/bin/env python3

"""Play a sound file.

This only reads a certain number of blocks at a time into memory,
therefore it can handle very long files and also files with many
channels.

NumPy and the soundfile module (http://PySoundFile.rtfd.io/) must be
installed for this to work.

"""
from __future__ import division
from __future__ import print_function
import argparse
try:
    import queue  # Python 3.x
except ImportError:
    import Queue as queue  # Python 2.x
import sys
import threading

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('filename', help='audio file to be played back')
parser.add_argument(
    '-b', '--buffersize', type=int, default=10,
    help='number of blocks used for buffering (default: %(default)s)')
parser.add_argument('-c', '--clientname', default='file player',
                    help='JACK client name')
parser.add_argument('-m', '--manual', action='store_true',
                    help="don't connect to output ports automatically")
args = parser.parse_args()
if args.buffersize < 1:
    parser.error('buffersize must be at least 1')

callback2disk = queue.Queue(maxsize=1)
disk2callback = queue.Queue(maxsize=1)
event = threading.Event()


def print_error(*args):
    print(*args, file=sys.stderr)


def xrun(delay):
    print_error("An xrun occured, increase JACK's period size?")


def shutdown(status, reason):
    print_error('JACK shutdown!')
    print_error('status:', status)
    print_error('reason:', reason)
    event.set()


def stop_callback(msg=''):
    if msg:
        print_error(msg)
    for port in client.outports:
        port.get_array().fill(0)
    event.set()
    raise jack.CallbackExit


def process(frames):
    global callback_buffer, callback_counter
    if frames != blocksize:
        stop_callback('blocksize must not be changed, I quit!')
    if callback_counter == 0:
        try:
            callback2disk.put_nowait(callback_buffer)
            callback_buffer, callback_counter = disk2callback.get_nowait()
        except (queue.Full, queue.Empty):
            stop_callback('Buffer error: increase buffersize?')
        if callback_counter == 0:  # Playback is finished
            stop_callback()
    idx = (args.buffersize - callback_counter) * blocksize
    block = callback_buffer[idx:idx + blocksize]
    for channel, port in zip(block.T, client.outports):
        port.get_array()[:] = channel
    callback_counter -= 1


try:
    import jack
    import numpy as np
    import soundfile as sf

    client = jack.Client(args.clientname)
    blocksize = client.blocksize
    samplerate = client.samplerate
    client.set_xrun_callback(xrun)
    client.set_shutdown_callback(shutdown)
    client.set_process_callback(process)

    with sf.SoundFile(args.filename) as f:
        block_generator = f.blocks(blocksize=blocksize, dtype='float32',
                                   always_2d=True, fill_value=0)

        def fill_buffer(buf):
            nr = -1  # For the case that block_generator is already exhausted
            for nr, block in zip(range(args.buffersize), block_generator):
                idx = nr * blocksize
                buf[idx:idx+blocksize] = block
            return nr + 1  # Number of valid blocks, the rest is garbage

        # Initialize first audio buffer to be played back
        buffer = np.empty([blocksize * args.buffersize, f.channels])
        valid_blocks = fill_buffer(buffer)
        disk2callback.put_nowait((buffer, valid_blocks))

        # Initialize second buffer
        callback_buffer = np.empty([blocksize * args.buffersize, f.channels])
        callback_counter = 0

        for ch in range(f.channels):
            client.outports.register('out_{0}'.format(ch + 1))

        with client:
            if not args.manual:
                target_ports = client.get_ports(
                    is_physical=True, is_input=True, is_audio=True)
                if len(client.outports) == 1 and len(target_ports) > 1:
                    # Connect mono file to stereo output
                    client.outports[0].connect(target_ports[0])
                    client.outports[0].connect(target_ports[1])
                else:
                    for source, target in zip(client.outports, target_ports):
                        source.connect(target)

            timeout = blocksize * args.buffersize / samplerate
            while valid_blocks:
                buffer = callback2disk.get(timeout=timeout)
                valid_blocks = fill_buffer(buffer)
                disk2callback.put((buffer, valid_blocks), timeout=timeout)
            event.wait()
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except (queue.Empty, queue.Full):
    # A timeout occured, i.e. there was an error in the callback
    parser.exit(1)
except Exception as e:
    parser.exit(e)
