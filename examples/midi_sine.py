#!/usr/bin/env python3
"""Very basic MIDI synthesizer.

This only works in Python 3.x because it uses memoryview.cast() and a
few other sweet Python-3-only features.

This is inspired by the JACK example program "jack_midisine":
http://github.com/jackaudio/jack2/blob/master/example-clients/midisine.c

But it is actually better:

+ ASR envelope
+ unlimited polyphony (well, "only" limited by CPU and memory)
+ arbitrary many MIDI events per block
+ can handle NoteOn and NoteOff event of the same pitch in one block

It is also worse:

- horribly inefficient (dynamic allocations, sample-wise processing)
- unpredictable because of garbage collection (?)

It sounds a little better than the original, but still quite boring.

"""
import jack
import math
import operator
import threading

# First 4 bits of status byte:
NOTEON = 0x9
NOTEOFF = 0x8

attack = 0.01  # seconds
release = 0.2  # seconds

fs = None
voices = {}

client = jack.Client("MIDI-Sine")
midiport = client.midi_inports.register("midi_in")
audioport = client.outports.register("audio_out")
event = threading.Event()


def m2f(note):
    """Convert MIDI note number to frequency in Hertz.

    See https://en.wikipedia.org/wiki/MIDI_Tuning_Standard.

    """
    return 2 ** ((note - 69) / 12) * 440


class Voice:

    def __init__(self, pitch):
        self.time = 0
        self.time_increment = m2f(pitch) / fs
        self.weight = 0

        self.target_weight = 0
        self.weight_step = 0
        self.compare = None

    def trigger(self, vel):
        if vel:
            dur = attack * fs
        else:
            dur = release * fs
        self.target_weight = vel / 127
        self.weight_step = (self.target_weight - self.weight) / dur
        self.compare = operator.ge if self.weight_step > 0 else operator.le

    def update(self):
        """Increment weight."""
        if self.weight_step:
            self.weight += self.weight_step
            if self.compare(self.weight, self.target_weight):
                self.weight = self.target_weight
                self.weight_step = 0


@client.set_process_callback
def process(frames):
    """Main callback."""
    events = {}
    buf = memoryview(audioport.get_buffer()).cast('f')
    for offset, data in midiport.incoming_midi_events():
        if len(data) == 3:
            status, pitch, vel = bytes(data)
            # MIDI channel number is ignored!
            status >>= 4
            if status == NOTEON and vel > 0:
                events.setdefault(offset, []).append((pitch, vel))
            elif status in (NOTEON, NOTEOFF):
                # NoteOff velocity is ignored!
                events.setdefault(offset, []).append((pitch, 0))
            else:
                pass  # ignore
        else:
            pass  # ignore
    for i in range(len(buf)):
        buf[i] = 0
        try:
            eventlist = events[i]
        except KeyError:
            pass
        else:
            for pitch, vel in eventlist:
                if pitch not in voices:
                    if not vel:
                        break
                    voices[pitch] = Voice(pitch)
                voices[pitch].trigger(vel)
        for voice in voices.values():
            voice.update()
            if voice.weight > 0:
                buf[i] += voice.weight * math.sin(2 * math.pi * voice.time)
                voice.time += voice.time_increment
                if voice.time >= 1:
                    voice.time -= 1
    dead = [k for k, v in voices.items() if v.weight <= 0]
    for pitch in dead:
        del voices[pitch]


@client.set_samplerate_callback
def samplerate(samplerate):
    global fs
    fs = samplerate
    voices.clear()


@client.set_shutdown_callback
def shutdown(status, reason):
    print("JACK shutdown:", reason, status)
    event.set()


with client:
    print("Press Ctrl+C to stop")
    try:
        event.wait()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
