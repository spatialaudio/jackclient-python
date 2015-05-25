#!/usr/bin/env python3

"""Create a JACK client that prints a lot of information with methods.

This client is like chatty_client in functionality but also defines a class
which has a lot of overridable methods (instead of using set_*_callback
all the time).

"""
import jack

class PythonicClient(jack.Client):
    def __init__(self, name, method_callbacks=True, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        if method_callbacks:
            self.set_method_callbacks()

    def set_method_callbacks(self):
        # NOTE: these are actually jack lib global, if one instanciates more
        # than one clients, only the last one's methods will get these called
        jack.set_error_function(self.error_function)
        jack.set_info_function(self.info_function)

        # per jack client instance callbacks
        self.set_blocksize_callback(self.on_blocksize_change)
        self.set_client_registration_callback(self.on_client_registration)
        self.set_freewheel_callback(self.on_freewheel_change)
        self.set_graph_order_callback(self.on_graph_order_change)
        self.set_port_connect_callback(self.on_port_connect)
        self.set_port_registration_callback(self.on_port_registration)
        self.set_port_rename_callback(self.on_port_rename)
        self.set_process_callback(self.process)
        self.set_samplerate_callback(self.on_samplerate_change)
        self.set_shutdown_callback(self.on_shutdown)
        self.set_xrun_callback(self.on_xrun)

    def error_function(self, message):
        print("Jack Error:", message)

    def info_function(self, message):
        print("Jack Info:", message)

    def on_blocksize_change(self, blocksize):
        pass

    def on_client_registration(self, name, register):
        pass

    def on_freewheel_change(self, starting):
        pass

    def on_graph_order_change(self):
        pass

    def on_port_connect(self, a, b, connect):
        pass

    def on_port_registration(self, port, register):
        pass

    def on_port_rename(self, port, old, new):
        pass

    def process(self, frames):
        pass

    def on_samplerate_change(self, samplerate):
        pass

    def on_shutdown(self, status, reason):
        pass

    def on_xrun(self, delayed_usecs):
        pass

class ChattyClient(PythonicClient):
    def __init__(self, name="Chatty-Client", *args, **kwargs):
        print("starting chatty client")
        super().__init__(name, method_callbacks=False, *args, **kwargs)

        if self.status.server_started:
            print("JACK server was started")
        else:
            print("JACK server was already running")
        if self.status.name_not_unique:
            print("unique client name generated:", self.name)

        print("setting error/info functions and registering callbacks")
        self.set_method_callbacks()

    def error_function(self, msg):
        print("Error:", msg)

    def info_function(self, msg):
        print("Info:", msg)

    def on_shutdown(self, status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)

    def on_freewheel_change(self, starting):
        print(["stopping", "starting"][starting], "freewheel mode")

    def on_blocksize_change(self, blocksize):
        print("blocksize changed to", blocksize)

    def on_samplerate_change(self, samplerate):
        print("samplerate changed to", samplerate)

    def on_client_registration(self, name, register):
        print("client", repr(name), ["unregistered", "registered"][register])

    def on_port_connect(self, a, b, connect):
        print(["disconnected", "connected"][connect], a, "and", b)

    def on_port_registration(self, port, register):
        print(repr(port), ["unregistered", "registered"][register])

    def on_port_rename(self, port, old, new):
        print("renamed", port, "from", repr(old), "to", repr(new))

    def on_graph_order_change(self):
        print("graph order change")

    def on_xrun(self, delayed_usecs):
        print("xrun; delay", delayed_usecs, "microseconds")

    def activate(self):
        print("activating JACK")
        super().activate()

client = ChattyClient("Chatty-Client")

with client:
    print("#" * 80)
    print("press Return to quit")
    print("#" * 80)
    input()
    print("closing JACK")
