"""Mock module for Sphinx autodoc."""


class FFI(object):
    def cdef(self, _):
        pass

    def dlopen(self, _):
        return self

    NULL = NotImplemented

    JackTransportStopped = 0
    JackTransportRolling = 1
    JackTransportStarting = 3
    JackTransportNetStarting = 4
