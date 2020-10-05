Installation
============

.. image:: https://badge.fury.io/py/JACK-Client.svg
   :target: https://pypi.org/project/JACK-Client/

You can use ``pip`` to install the ``jack`` module::

   python3 -m pip install JACK-Client

Depending on your Python installation (see `Requirements`_ below),
you may have to use ``python`` instead of ``python3``.
If you have installed the module already, you can use the ``--upgrade`` flag to
get the newest release.

To un-install, use::

   python3 -m pip uninstall JACK-Client

Requirements
------------

You'll need some software packages in order to install and use the ``jack``
module.  Some of those might already be installed on your system and some are
automatically installed when you use the aforementioned ``pip`` command.

Python:
   Of course, you'll need Python_.  More specifically, you'll need Python 3.
   If you don't have Python installed yet, you should get one of the
   distributions which already include CFFI and NumPy (and many other useful
   things), e.g. Anaconda_ or WinPython_.

pip/setuptools:
   Those are needed for the installation of the Python module and its
   dependencies.  Most systems will have these installed already, but if not,
   you should install it with your package manager or you can download and
   install ``pip`` and ``setuptools`` as described on the `pip installation`_
   page.
   If you happen to have ``pip`` but not ``setuptools``, use this command::

      python3 -m pip install setuptools

   To upgrade to a newer version of an already installed package (including
   ``pip`` itself), use the ``--upgrade`` flag.

CFFI:
   The `C Foreign Function Interface for Python`_ is used to access the C-API
   of the JACK library from within Python.  It is supported on CPython
   and is distributed with PyPy_.  It will be automatically installed
   when installing the ``JACK-Client`` package with ``pip``.
   If you prefer, you can also install it with your package
   manager (the package might be called ``python3-cffi`` or similar).

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
   The only place where NumPy is needed is `jack.OwnPort.get_array()`
   (and you can use `jack.OwnPort.get_buffer()` as a NumPy-less alternative).
   If you need NumPy, you can install it with your package manager or use a
   Python distribution that already includes NumPy (see above).
   You can also install NumPy with ``pip``, but depending on your platform, this
   might require a compiler and several additional libraries::

      python3 -m pip install NumPy

.. _JACK: https://jackaudio.org/
.. _NumPy: https://numpy.org/
.. _Python: https://www.python.org/
.. _Anaconda: https://www.anaconda.com/products/individual#Downloads
.. _WinPython: http://winpython.github.io/
.. _C Foreign Function Interface for Python: https://cffi.readthedocs.org/
.. _PyPy: https://www.pypy.org/
.. _JACK download page: https://jackaudio.org/downloads/
.. _pip installation: https://pip.pypa.io/en/latest/installing/
