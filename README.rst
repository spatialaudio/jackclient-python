JACK Audio Connection Kit (JACK) Client for Python
==================================================

This Python module provides bindings for the JACK_ library.

Documentation:
  http://jackclient-python.rtfd.org/

Code:
  http://github.com/spatialaudio/jackclient-python/

Python Package Index:
  http://pypi.python.org/pypi/JACK-Client/

Requirements
------------

Python:
   Of course, you'll need Python_.
   Any version where CFFI (see below) is supported should work.
   If you don't have Python installed yet, you should get one of the
   distributions which already include CFFI (and many other useful things),
   e.g. Anaconda_.

CFFI:
   The `C Foreign Function Interface for Python`_ is used to access the C-API
   of the JACK library from within Python.  It supports CPython 2.6, 2.7, 3.x;
   and is distributed with PyPy_ 2.0 beta2 or later.
   You should install it with your package manager (if it's not installed
   already), or you can get it with pip_::

      pip install cffi --user

JACK library:
   The JACK_ library must be installed on your system (and CFFI must be able
   to find it).  Again, you should use your package manager to install it.
   Make sure you install the JACK daemon (called ``jackd``). This will also
   install the JACK library package.
   If you prefer, you can of course also download the sources and compile
   everything locally.

setuptools:
   This is needed for the installation of the Python module.  Most systems will
   have this installed already, but if not, you can install it with your
   package manager or you can get it with pip_::

      pip install setuptools --user

.. _Python: http://www.python.org/
.. _Anaconda: http://docs.continuum.io/anaconda/
.. _C Foreign Function Interface for Python: http://cffi.readthedocs.org/
.. _PyPy: http://pypy.org/
.. _JACK: http://jackaudio.org/
.. _pip: http://www.pip-installer.org/en/latest/installing.html

Installation
------------

Once you have installed the above-mentioned dependencies, you can use pip_
to download and install the latest release with a single command::

   pip install JACK-Client --user

If you want to install it system-wide for all users (assuming you have the
necessary rights), you can just drop the ``--user`` option.

To un-install, use::

   pip uninstall JACK-Client

If you prefer, you can also download the package from PyPI_, extract it, change
to the main directory and install it using::

   python setup.py install --user

.. _PyPI: http://pypi.python.org/pypi/JACK-Client/

If you want to get the newest development version from Github_::

   git clone https://github.com/spatialaudio/jackclient-python.git
   cd jackclient-python
   python setup.py develop --user

.. _Github: http://github.com/spatialaudio/jackclient-python/

This way, your installation always stays up-to-date, even if you pull new
changes from the Github repository.

If you prefer, you can also replace the last command with::

   pip install --user -e .

... where ``-e`` stands for ``--editable``.

If you want to avoid installation altogether, you can simply copy ``jack.py``
to your working directory (or to any directory in your Python path).

Usage
-----

First, import the module::

   import jack

Then, you most likely want to create a new JACK client::

   client = jack.Client("MyGreatClient")

You probably want to create some input and output ports, too::

   client.inports.register("input_1")
   client.outports.register("output_1")

These functions return the newly created port, so you can save it for later::

   in2 = client.inports.register("input_2")
   out2 = client.outports.register("output_2")

To see what you can do with the returned objects, have a look at the
documentation of the class `jack.OwnPort`.

You can also check what other JACK ports are available::

   portlist = client.get_ports()

If you want, you can also set all kinds of callback functions, for details see
the API documentation for the class `jack.Client`.

Once you are ready to run, you should activate your client::

   client.activate()

Once the client is activated, you can make connections (this isn't possible
before activating the client)::

   client.connect("system:capture_1", "MyGreatClient:input_1")
   client.connect("MyGreatClient:output_1", "system:playback_1")

You can also use the port objects from before instead of port names::

   client.connect(out2, "system:playback_2")
   in2.connect("system:capture_2")

You can also disconnect ports, there are again several possibilities::

   client.disconnect("system:capture_1", "MyGreatClient:input_1")
   client.disconnect(out2, "system:playback_2")
   # disconnect all connections with in2:
   in2.disconnect()

If you don't need your ports anymore, you can un-register them::

   in2.unregister()
   # unregister all output ports:
   client.outports.clear()

Finally, you can de-activate your JACK client and close it::

   client.deactivate()
   client.close()
