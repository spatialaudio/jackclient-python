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
