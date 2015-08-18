#!/usr/bin/env python3

"""Create a JACK client that prints a lot of information.

This client registers all possible callbacks (except the process
callback and the timebase callback, which would be just too much noise)
and prints some information whenever they are called.

"""
from __future__ import print_function  # only needed for Python 2.x
import jack

print("setting error/info functions")


@jack.set_error_function
def error(msg):
    print("Error:", msg)


@jack.set_info_function
def info(msg):
    print("Info:", msg)


print("starting chatty client")

client = jack.Client("Chatty-Client")

if client.status.server_started:
    print("JACK server was started")
else:
    print("JACK server was already running")
if client.status.name_not_unique:
    print("unique client name generated:", client.name)


print("registering callbacks")


@client.set_shutdown_callback
def shutdown(status, reason):
    print("JACK shutdown!")
    print("status:", status)
    print("reason:", reason)


@client.set_freewheel_callback
def freewheel(starting):
    print(["stopping", "starting"][starting], "freewheel mode")


@client.set_blocksize_callback
def blocksize(blocksize):
    print("setting blocksize to", blocksize)


@client.set_samplerate_callback
def samplerate(samplerate):
    print("setting samplerate to", samplerate)


@client.set_client_registration_callback
def client_registration(name, register):
    print("client", repr(name), ["unregistered", "registered"][register])


@client.set_port_registration_callback
def port_registration(port, register):
    print(repr(port), ["unregistered", "registered"][register])


@client.set_port_connect_callback
def port_connect(a, b, connect):
    print(["disconnected", "connected"][connect], a, "and", b)


try:
    @client.set_port_rename_callback
    def port_rename(port, old, new):
        print("renamed", port, "from", repr(old), "to", repr(new))
except AttributeError:
    print("Could not register port rename callback (not available on JACK1).")


@client.set_graph_order_callback
def graph_order():
    print("graph order changed")


@client.set_xrun_callback
def xrun(delay):
    print("xrun; delay", delay, "microseconds")


print("activating JACK")
with client:
    print("#" * 80)
    print("press Return to quit")
    print("#" * 80)
    input()
    print("closing JACK")
