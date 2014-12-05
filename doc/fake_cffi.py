"""Mock module for Sphinx autodoc."""


class FFI(object):
    def cdef(self, _):
        pass

    def dlopen(self, _):
        return self

    NULL = NotImplemented
