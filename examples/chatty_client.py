#!/usr/bin/env python3

"""Create a JACK client that prints a lot of information.

This client registers all possible callbacks (except the process
callback, which would be just too much noise) and prints some
information whenever they are called.

"""
from __future__ import print_function  # only needed for Python 2.x
import jack


def error(msg):
    print("Error:", msg)


def info(msg):
    print("Info:", msg)


print("setting error/info functions")
jack.set_error_function(error)
jack.set_info_function(info)


print("starting chatty client")

client = jack.Client("Chatty-Client")

if client.status.server_started:
    print("JACK server was started")
else:
    print("JACK server was already running")
if client.status.name_not_unique:
    print("unique client name generated:", client.name)


print("registering callbacks")


def shutdown(status, reason, userdata):
    print("JACK shutdown!")
    print("status:", status)
    print("reason:", reason)

client.set_shutdown_callback(shutdown)


def freewheel(starting, userdata):
    print(["stopping", "starting"][starting], "freewheel mode")

client.set_freewheel_callback(freewheel)


def blocksize(blocksize, userdata):
    print("setting blocksize to", blocksize)
    return jack.SUCCESS

client.set_blocksize_callback(blocksize)


def samplerate(samplerate, userdata):
    print("setting samplerate to", samplerate)
    return jack.SUCCESS

client.set_samplerate_callback(samplerate)


def client_registration(name, register, userdata):
    print("client", repr(name), ["unregistered", "registered"][register])

client.set_client_registration_callback(client_registration)


def port_registration(port, register, userdata):
    print(repr(port), ["unregistered", "registered"][register])

client.set_port_registration_callback(port_registration)


def port_connect(a, b, connect, userdata):
    print(["disconnected", "connected"][connect], a, "and", b)

client.set_port_connect_callback(port_connect)


def port_rename(port, old, new, userdata):
    print("renamed", port, "from", repr(old), "to", repr(new))
    return jack.SUCCESS

client.set_port_rename_callback(port_rename)


def graph_order(userdata):
    print("graph order changed")
    return jack.SUCCESS

client.set_graph_order_callback(graph_order)


def xrun(userdata):
    print("xrun; delay", client.xrun_delayed_usecs, "microseconds")
    return jack.SUCCESS

client.set_xrun_callback(xrun)

print("activating JACK")
with client:
    print("#" * 80)
    print("press Return to quit")
    print("#" * 80)
    input()
    print("closing JACK")
