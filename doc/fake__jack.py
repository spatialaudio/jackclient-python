"""Mock module for Sphinx autodoc."""


import ctypes


# Monkey-patch ctypes to disable searching for JACK
ctypes.util.find_library = lambda _: NotImplemented


class Fake(object):

    NULL = NotImplemented

    JackTransportStopped = 0
    JackTransportRolling = 1
    JackTransportStarting = 3
    JackTransportNetStarting = 4

    def dlopen(self, _):
        return self


ffi = Fake()
