Installation
============

Requirements
------------

The JACK_ library must be installed on your system (and CFFI must be able
to find it).  You should use your package manager to install it.
Make sure you install the JACK daemon (called ``jackd``). This will also
install the JACK library package.
If you don't have a package manager, you can try one of the binary installers
from the `JACK download page`_.
If you prefer, you can of course also download the sources and compile
everything locally.

You'll also need to install Python_ if you haven't yet done so.
There are many ways to install Python,
and you can use any way you like,
however, we recommend using uv_ as shown in the steps below.

You can install ``uv`` with your favorite package manager,
or by one of the other methods described at
https://docs.astral.sh/uv/getting-started/installation/.

If you don't like ``uv``, no problem!
You can also use Python's official packaging tool pip_ or any other third-party tool,
as long as it can install `the JACK-Client package`_.

.. _JACK: https://jackaudio.org/
.. _JACK download page: https://jackaudio.org/downloads/
.. _Python: https://www.python.org/
.. _uv: https://docs.astral.sh/uv/
.. _pip: https://packaging.python.org/en/latest/tutorials/installing-packages/
.. _the JACK-Client package: https://pypi.org/project/JACK-Client/
.. _NumPy: http://www.numpy.org/


Installation
------------

First, create a new directory wherever you want, change into it, then run::

    uv init --bare

This will create a file named ``pyproject.toml`` for you.
Use the ``--help`` flag to see other options.

The ``jack`` module can now be installed with::

    uv add JACK-Client

This will also create a file named ``uv.lock``, which tracks the exact versions
of all installed packages.

NumPy_ is only needed if you want to access the input and output buffers in
the process callback as NumPy arrays.
The only place where NumPy is needed is `jack.OwnPort.get_array()`
(and you can use `jack.OwnPort.get_buffer()` as a NumPy-less alternative).
If you need NumPy, you can install it with::

    uv add numpy

Similarly, you can install other Python-related tools::

    uv add ...

Once everything is installed, you can start working with the editor/IDE/tool
of your choice by simply prefixing it with ``uv run``, for example::

    uv run python

If you have a Python script (for inspiration see :doc:`examples`),
e.g. ``my_script.py``, you can run it with::

    uv run my_script.py

If you want to install the latest development version of the JACK-Client,
have a look at :doc:`contributing`.
