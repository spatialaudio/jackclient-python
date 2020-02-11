Version 0.5.2 (2020-02-11):
 * new module constants: ``jack.POSITION_*``
 * new examples: ``timebase_master.py`` and ``transporter.py``,
   thanks to Christopher Arndt
 * new `jack.JackError` subclasses: `jack.JackErrorCode` and `jack.JackOpenError`,
   thanks to Christopher Arndt

Version 0.5.1 (2019-11-07):
 * `jack.Client.release_timebase()`, thanks to Christopher Arndt

Version 0.5.0 (2019-07-18):
 * drop Python 2 support
 * support for metadata API, with the help of Christopher Arndt
 * support for slow-sync clients

Version 0.4.6 (2019-02-09):
 * ``midi_file_player.py`` example

Version 0.4.5 (2018-09-02):
 * Fix issue #54; other minor improvements

Version 0.4.4 (2018-02-19):
 * `Port.set_alias()`, `Port.unset_alias()` and `Port.aliases`, thanks to
   Jośe Fernando Moyano

Version 0.4.3 (2017-12-30):
 * switch to CFFI out-of-line ABI mode (to reduce import time)

Version 0.4.2 (2016-11-05):
 * new examples: ``showtime.py``, ``midi_sine_numpy.py`` and ``play_file.py``
 * new option ``only_available`` for port callbacks

Version 0.4.1 (2016-05-24):
 * new property `jack.Client.transport_frame`, deprecating
   `jack.Client.transport_locate()`

Version 0.4.0 (2015-09-17):
 * new argument to xrun callback (see `jack.Client.set_xrun_callback()`),
   `jack.Client.xrun_delayed_usecs` was removed
 * `jack.Client.transport_reposition_struct()`
 * callbacks no longer have to return anything, instead they can raise
   `jack.CallbackExit` on error
 * ``midi_sine.py`` example

Version 0.3.0 (2015-07-16):
 * `jack.RingBuffer`, implemented by Alexandru Stan
 * `jack.Client.set_timebase_callback()`, `jack.Client.transport_query()`,
   `jack.Client.transport_query_struct()`, with the help of Julien Acroute
 * `jack.Client.transport_state`, `jack.STOPPED`, `jack.ROLLING`,
   `jack.STARTING`, `jack.NETSTARTING`, `jack.position2dict()`
 * the *userdata* argument was removed from all callbacks
 * compatibility with the official JACK installer for Windows, thanks to Julien
   Acroute

Version 0.2.0 (2015-02-23):
 * MIDI support (`jack.MidiPort`, `jack.OwnMidiPort`,
   `jack.Client.midi_inports`, `jack.Client.midi_outports`, ...)
 * ignore errors in `jack.Client.deactivate()` by default, can be overridden
 * optional argument to `jack.OwnPort.disconnect()`
 * several examples (``chatty_client.py``, ``thru_client.py``,
   ``midi_monitor.py`` and ``midi_chords.py``)
 * `jack.Port.is_physical`, courtesy of Alexandru Stan
 * `jack.Status`

Version 0.1.0 (2014-12-15):
   Initial release
