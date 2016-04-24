JACK Audio Connection Kit (JACK) Client for Python
==================================================

This Python module provides bindings for the JACK_ library.

Documentation:
   http://jackclient-python.rtfd.org/

Code:
   http://github.com/spatialaudio/jackclient-python/

Python Package Index:
   http://pypi.python.org/pypi/JACK-Client/

License:
   MIT -- see the file ``LICENSE`` for details.

Requirements
------------

Python:
   Of course, you'll need Python_.
   Any version where CFFI (see below) is supported should work.
   If you don't have Python installed yet, you should get one of the
   distributions which already include CFFI and NumPy (and many other useful
   things), e.g. Anaconda_ or WinPython_.

pip/setuptools:
   Those are needed for the installation of the Python module and its
   dependencies.  Most systems will have these installed already, but if not,
   you should install it with your package manager or you can download and
   install pip and setuptools as described on the `pip installation`_ page.
   If you happen to have pip but not setuptools, use this command::

      pip install setuptools --user

CFFI:
   The `C Foreign Function Interface for Python`_ is used to access the C-API
   of the JACK library from within Python.  It supports CPython 2.6, 2.7, 3.x;
   and is distributed with PyPy_ 2.0 beta2 or later.
   You should install it with your package manager (if it's not installed
   already), or you can get it with::

      pip install cffi --user

JACK library:
   The JACK_ library must be installed on your system (and CFFI must be able
   to find it).  Again, you should use your package manager to install it.
   Make sure you install the JACK daemon (called ``jackd``). This will also
   install the JACK library package.
   If you don't have a package manager, you can try one of the binary installers
   from the `JACK download page`_.
   If you prefer, you can of course also download the sources and compile
   everything locally.

NumPy (optional):
   NumPy_ is only needed if you want to access the input and output buffers in
   the process callback as NumPy arrays.
   The only place where NumPy is needed is `jack.OwnPort.get_array()`.
   If you need NumPy, you should install it with your package manager or use a
   Python distribution that already includes NumPy (see above).
   Installing NumPy with pip requires a compiler and several additional
   libraries and is therefore not recommended for beginners.

.. _JACK: http://jackaudio.org/
.. _NumPy: http://www.numpy.org/
.. _Python: http://www.python.org/
.. _Anaconda: http://docs.continuum.io/anaconda/
.. _WinPython: http://winpython.github.io/
.. _C Foreign Function Interface for Python: http://cffi.readthedocs.org/
.. _PyPy: http://pypy.org/
.. _JACK download page: http://jackaudio.org/downloads/
.. _pip installation: http://www.pip-installer.org/en/latest/installing.html

Installation
------------

Once you have installed the above-mentioned dependencies, you can use pip
to download and install the latest release with a single command::

   pip install JACK-Client --user

If you want to install it system-wide for all users (assuming you have the
necessary rights), you can just drop the ``--user`` option.

To un-install, use::

   pip uninstall JACK-Client

If you want to avoid installation altogether, you can simply copy ``jack.py``
to your working directory (or to any directory in your Python path).

Usage
-----

First, import the module:

>>> import jack

Then, you most likely want to create a new `jack.Client`:

>>> client = jack.Client("MyGreatClient")

You probably want to create some audio input and output ports, too:

>>> client.inports.register("input_1")
jack.OwnPort('MyGreatClient:input_1')
>>> client.outports.register("output_1")
jack.OwnPort('MyGreatClient:output_1')

As you can see, these functions return the newly created port.
If you want, you can save it for later:

>>> in2 = client.inports.register("input_2")
>>> out2 = client.outports.register("output_2")

To see what you can do with the returned objects, have a look at the
documentation of the class `jack.OwnPort`.

In case you forgot, you should remind yourself about the ports you just created:

>>> client.inports
[jack.OwnPort('MyGreatClient:input_1'), jack.OwnPort('MyGreatClient:input_2')]
>>> client.outports
[jack.OwnPort('MyGreatClient:output_1'), jack.OwnPort('MyGreatClient:output_2')]

Have a look at the documentation of the class `jack.Ports` to get more detailed
information about these lists of ports.

If you have selected an appropriate driver in your JACK settings, you can also
create MIDI ports:

>>> client.midi_inports.register("midi_in")
jack.OwnMidiPort('MyGreatClient:midi_in')
>>> client.midi_outports.register("midi_out")
jack.OwnMidiPort('MyGreatClient:midi_out')

You can check what other JACK ports are available (your output may be
different):

>>> client.get_ports()  # doctest: +SKIP
[jack.Port('system:capture_1'),
 jack.Port('system:capture_2'),
 jack.Port('system:playback_1'),
 jack.Port('system:playback_2'),
 jack.MidiPort('system:midi_capture_1'),
 jack.MidiPort('system:midi_playback_1'),
 jack.OwnPort('MyGreatClient:input_1'),
 jack.OwnPort('MyGreatClient:output_1'),
 jack.OwnPort('MyGreatClient:input_2'),
 jack.OwnPort('MyGreatClient:output_2'),
 jack.OwnMidiPort('MyGreatClient:midi_in'),
 jack.OwnMidiPort('MyGreatClient:midi_out')]

Note that the ports you created yourself are of type `jack.OwnPort` and
`jack.OwnMidiPort`, while other ports are merely of type `jack.Port` and
`jack.MidiPort`, respectively.

You can also be more specific when looking for ports:

>>> client.get_ports(is_audio=True, is_output=True, is_physical=True)
[jack.Port('system:capture_1'), jack.Port('system:capture_2')]

You can even use regular expressions to search for ports:

>>> client.get_ports("Great.*2$")
[jack.OwnPort('MyGreatClient:input_2'), jack.OwnPort('MyGreatClient:output_2')]

If you want, you can also set all kinds of callback functions for your client.
For details see the documentation for the class `jack.Client` and the example
applications in the ``examples/`` directory.

Once you are ready to run, you should activate your client:

>>> client.activate()

As soon as the client is activated, you can make connections (this isn't
possible before activating the client):

>>> client.connect("system:capture_1", "MyGreatClient:input_1")
>>> client.connect("MyGreatClient:output_1", "system:playback_1")

You can also use the port objects from before instead of port names:

>>> client.connect(out2, "system:playback_2")
>>> in2.connect("system:capture_2")

Use `jack.Client.get_all_connections()` to find out which other ports are
connected to a given port.
If you own the port, you can also use `jack.OwnPort.connections`.

>>> client.get_all_connections("system:playback_1")
[jack.OwnPort('MyGreatClient:output_1')]
>>> out2.connections
[jack.Port('system:playback_2')]

Of course you can also disconnect ports, there are again several possibilities:

>>> client.disconnect("system:capture_1", "MyGreatClient:input_1")
>>> client.disconnect(out2, "system:playback_2")
>>> in2.disconnect()  # disconnect all connections with in2

If you don't need your ports anymore, you can un-register them:

>>> in2.unregister()
>>> client.outports.clear()  # unregister all audio output ports

Finally, you can de-activate your JACK client and close it:

>>> client.deactivate()
>>> client.close()
