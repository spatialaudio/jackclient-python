#!/usr/bin/env python3
"""Very basic MIDI synthesizer.

This does the same as midi_sine.py, but it uses NumPy and block
processing.  It is therefore much more efficient.  But there are still
many allocations and dynamically growing and shrinking data structures.

"""
import jack
import numpy as np
import threading

# First 4 bits of status byte:
NOTEON = 0x9
NOTEOFF = 0x8

attack_seconds = 0.01
release_seconds = 0.2

attack = None
release = None
fs = None
voices = {}

client = jack.Client('MIDI-Sine-NumPy')
midiport = client.midi_inports.register('midi_in')
audioport = client.outports.register('audio_out')
event = threading.Event()


def m2f(note):
    """Convert MIDI note number to frequency in Hertz.

    See https://en.wikipedia.org/wiki/MIDI_Tuning_Standard.

    """
    return 2 ** ((note - 69) / 12) * 440


def update_envelope(envelope, begin, target, vel):
    """Helper function to calculate envelopes.

    envelope: array of velocities, will be mutated
    begin: sample index where ramp begins
    target: sample index where *vel* shall be reached
    vel: final velocity value

    If the ramp goes beyond the blocksize, it is supposed to be
    continued in the next block.

    A reference to *envelope* is returned, as well as the (unchanged)
    *vel* and the target index of the following block where *vel* shall
    be reached.

    """
    blocksize = len(envelope)
    old_vel = envelope[begin]
    slope = (vel - old_vel) / (target - begin + 1)
    ramp = np.arange(min(target, blocksize) - begin) + 1
    envelope[begin:target] = ramp * slope + old_vel
    if target < blocksize:
        envelope[target:] = vel
        target = 0
    else:
        target -= blocksize
    return envelope, vel, target


@client.set_process_callback
def process(blocksize):
    """Main callback."""

    # Step 1: Update/delete existing voices from previous block

    # Iterating over a copy because items may be deleted:
    for pitch in list(voices):
        envelope, vel, target = voices[pitch]
        if any([vel, target]):
            envelope[0] = envelope[-1]
            voices[pitch] = update_envelope(envelope, 0, target, vel)
        else:
            del voices[pitch]

    # Step 2: Create envelopes from the MIDI events of the current block

    for offset, data in midiport.incoming_midi_events():
        if len(data) == 3:
            status, pitch, vel = bytes(data)
            # MIDI channel number is ignored!
            status >>= 4
            if status == NOTEON and vel > 0:
                try:
                    envelope, _, _ = voices[pitch]
                except KeyError:
                    envelope = np.zeros(blocksize)
                voices[pitch] = update_envelope(
                    envelope, offset, offset + attack, vel)
            elif status in (NOTEON, NOTEOFF):
                # NoteOff velocity is ignored!
                try:
                    envelope, _, _ = voices[pitch]
                except KeyError:
                    print('NoteOff without NoteOn (ignored)')
                    continue
                voices[pitch] = update_envelope(
                    envelope, offset, offset + release, 0)
            else:
                pass  # ignore
        else:
            pass  # ignore

    # Step 3: Create sine tones, apply envelopes, add to output buffer

    buf = audioport.get_array()
    buf.fill(0)
    for pitch, (envelope, _, _) in voices.items():
        t = (np.arange(blocksize) + client.last_frame_time) / fs
        tone = np.sin(2 * np.pi * m2f(pitch) * t)
        buf += tone * envelope / 127


@client.set_samplerate_callback
def samplerate(samplerate):
    global fs, attack, release
    fs = samplerate
    attack = int(attack_seconds * fs)
    release = int(release_seconds * fs)
    voices.clear()


@client.set_shutdown_callback
def shutdown(status, reason):
    print('JACK shutdown:', reason, status)
    event.set()

with client:
    print('Press Ctrl+C to stop')
    try:
        event.wait()
    except KeyboardInterrupt:
        print('\nInterrupted by user')
