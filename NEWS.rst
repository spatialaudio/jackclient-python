Version 0.5.3 -- 2020-10-21 -- PyPI__ -- docs__ -- diff__
 * use ``jack_port_rename()`` instead of deprecated ``jack_port_set_name()``

__ https://pypi.org/project/JACK-Client/0.5.3/
__ https://jackclient-python.readthedocs.io/en/0.5.3/
__ https://github.com/spatialaudio/jackclient-python/compare/0.5.2...0.5.3

Version 0.5.2 -- 2020-02-11 -- PyPI__ -- docs__ -- diff__
 * new module constants: ``jack.POSITION_*``
 * new examples: ``timebase_master.py`` and ``transporter.py``,
   thanks to Christopher Arndt
 * new `jack.JackError` subclasses: `jack.JackErrorCode` and `jack.JackOpenError`,
   thanks to Christopher Arndt

__ https://pypi.org/project/JACK-Client/0.5.2/
__ https://jackclient-python.readthedocs.io/en/0.5.2/
__ https://github.com/spatialaudio/jackclient-python/compare/0.5.1...0.5.2

Version 0.5.1 -- 2019-11-07 -- PyPI__ -- docs__ -- diff__
 * `jack.Client.release_timebase()`, thanks to Christopher Arndt

__ https://pypi.org/project/JACK-Client/0.5.1/
__ https://jackclient-python.readthedocs.io/en/0.5.1/
__ https://github.com/spatialaudio/jackclient-python/compare/0.5.0...0.5.1

Version 0.5.0 -- 2019-07-18 -- PyPI__ -- docs__ -- diff__
 * drop Python 2 support
 * support for metadata API, with the help of Christopher Arndt
 * support for slow-sync clients

__ https://pypi.org/project/JACK-Client/0.5.0/
__ https://jackclient-python.readthedocs.io/en/0.5.0/
__ https://github.com/spatialaudio/jackclient-python/compare/0.4.6...0.5.0

Version 0.4.6 -- 2019-02-09 -- PyPI__ -- docs__ -- diff__
 * ``midi_file_player.py`` example

__ https://pypi.org/project/JACK-Client/0.4.6/
__ https://jackclient-python.readthedocs.io/en/0.4.6/
__ https://github.com/spatialaudio/jackclient-python/compare/0.4.5...0.4.6

Version 0.4.5 -- 2018-09-02 -- PyPI__ -- docs__ -- diff__
 * Fix issue #54; other minor improvements

__ https://pypi.org/project/JACK-Client/0.4.5/
__ https://jackclient-python.readthedocs.io/en/0.4.5/
__ https://github.com/spatialaudio/jackclient-python/compare/0.4.4...0.4.5

Version 0.4.4 -- 2018-02-19 -- PyPI__ -- docs__ -- diff__
 * `Port.set_alias()`, `Port.unset_alias()` and `Port.aliases`, thanks to
   Jośe Fernando Moyano

__ https://pypi.org/project/JACK-Client/0.4.4/
__ https://jackclient-python.readthedocs.io/en/0.4.4/
__ https://github.com/spatialaudio/jackclient-python/compare/0.4.3...0.4.4

Version 0.4.3 -- 2017-12-30 -- PyPI__ -- docs__ -- diff__
 * switch to CFFI out-of-line ABI mode (to reduce import time)

__ https://pypi.org/project/JACK-Client/0.4.3/
__ https://jackclient-python.readthedocs.io/en/0.4.3/
__ https://github.com/spatialaudio/jackclient-python/compare/0.4.2...0.4.3

Version 0.4.2 -- 2016-11-05 -- PyPI__ -- docs__ -- diff__
 * new examples: ``showtime.py``, ``midi_sine_numpy.py`` and ``play_file.py``
 * new option ``only_available`` for port callbacks

__ https://pypi.org/project/JACK-Client/0.4.2/
__ https://jackclient-python.readthedocs.io/en/0.4.2/
__ https://github.com/spatialaudio/jackclient-python/compare/0.4.1...0.4.2

Version 0.4.1 -- 2016-05-24 -- PyPI__ -- docs__ -- diff__
 * new property `jack.Client.transport_frame`, deprecating
   `jack.Client.transport_locate()`

__ https://pypi.org/project/JACK-Client/0.4.1/
__ https://jackclient-python.readthedocs.io/en/0.4.1/
__ https://github.com/spatialaudio/jackclient-python/compare/0.4.0...0.4.1

Version 0.4.0 -- 2015-09-17 -- PyPI__ -- docs__ -- diff__
 * new argument to xrun callback (see `jack.Client.set_xrun_callback()`),
   ``jack.Client.xrun_delayed_usecs`` was removed
 * `jack.Client.transport_reposition_struct()`
 * callbacks no longer have to return anything, instead they can raise
   `jack.CallbackExit` on error
 * ``midi_sine.py`` example

__ https://pypi.org/project/JACK-Client/0.4.0/
__ https://jackclient-python.readthedocs.io/en/0.4.0/
__ https://github.com/spatialaudio/jackclient-python/compare/0.3.0...0.4.0

Version 0.3.0 -- 2015-07-16 -- PyPI__ -- docs__ -- diff__
 * `jack.RingBuffer`, implemented by Alexandru Stan
 * `jack.Client.set_timebase_callback()`, `jack.Client.transport_query()`,
   `jack.Client.transport_query_struct()`, with the help of Julien Acroute
 * `jack.Client.transport_state`, `jack.STOPPED`, `jack.ROLLING`,
   `jack.STARTING`, `jack.NETSTARTING`, `jack.position2dict()`
 * the *userdata* argument was removed from all callbacks
 * compatibility with the official JACK installer for Windows, thanks to Julien
   Acroute

__ https://pypi.org/project/JACK-Client/0.3.0/
__ https://jackclient-python.readthedocs.io/en/0.3.0/
__ https://github.com/spatialaudio/jackclient-python/compare/0.2.0...0.3.0

Version 0.2.0 -- 2015-02-23 -- PyPI__ -- docs__ -- diff__
 * MIDI support (`jack.MidiPort`, `jack.OwnMidiPort`,
   `jack.Client.midi_inports`, `jack.Client.midi_outports`, ...)
 * ignore errors in `jack.Client.deactivate()` by default, can be overridden
 * optional argument to `jack.OwnPort.disconnect()`
 * several examples (``chatty_client.py``, ``thru_client.py``,
   ``midi_monitor.py`` and ``midi_chords.py``)
 * `jack.Port.is_physical`, courtesy of Alexandru Stan
 * `jack.Status`

__ https://pypi.org/project/JACK-Client/0.2.0/
__ https://jackclient-python.readthedocs.io/en/0.2.0/
__ https://github.com/spatialaudio/jackclient-python/compare/0.1.0...0.2.0

Version 0.1.0 -- 2014-12-15 -- PyPI__ -- docs__
   Initial release

__ https://pypi.org/project/JACK-Client/0.1.0/
__ https://jackclient-python.readthedocs.io/en/0.1.0/
