"""Mock module for Sphinx autodoc."""

import ctypes.util

old_find_library = ctypes.util.find_library


def new_find_library(name):
    if 'jack' in name.lower():
        return NotImplemented
    return old_find_library(name)


# Monkey-patch ctypes to disable searching for JACK
ctypes.util.find_library = new_find_library


class Fake(object):

    NULL = NotImplemented

    JackTransportStopped = 0
    JackTransportRolling = 1
    JackTransportStarting = 3
    JackTransportNetStarting = 4

    PropertyCreated = 0
    PropertyChanged = 1
    PropertyDeleted = 2

    JackPositionBBT = 0x10
    JackPositionTimecode = 0x20
    JackBBTFrameOffset = 0x40
    JackAudioVideoRatio = 0x80
    JackVideoFrameOffset = 0x100

    def dlopen(self, _):
        return self


ffi = Fake()
