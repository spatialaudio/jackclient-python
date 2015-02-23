Version 0.2.0 (2015-02-23):
 * MIDI support (`jack.MidiPort`, `jack.OwnMidiPort`,
   `jack.Client.midi_inports`, `jack.Client.midi_outports`, ...)
 * ignore errors in `jack.Client.deactivate()` by default, can be overridden
 * optional argument to `jack.OwnPort.disconnect()`
 * several examples (``chatty_client.py``, ``thru_client.py``,
   ``midi_monitor.py`` and ``midi_chords.py``)
 * `jack.Port.is_physical`, courtesy of Alexandru Stan
 * `jack.Status` class
 * some bug-fixes and refactorings, some documentation improvements

Version 0.1.0 (2014-12-15):
   Initial release
