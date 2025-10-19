Contributing
------------

If you find bugs, errors, omissions or other things that need improvement,
please create an issue or a pull request at
https://github.com/spatialaudio/jackclient-python.
Contributions are always welcome!

Instead of installing the latest release from PyPI_, you should get the
newest development version from GitHub_::

   git clone https://github.com/spatialaudio/jackclient-python.git
   cd jackclient-python
   uv sync
   uv run jack_build.py

This way, your installation always stays up-to-date, even if you pull new
changes from the GitHub repository.

.. _PyPI: https://pypi.org/project/JACK-Client/
.. _GitHub: https://github.com/spatialaudio/jackclient-python/

.. note::

   Whenever the file ``jack_build.py`` changes (either because you edited it or
   it was updated by pulling from GitHub or switching branches), you have to
   run the last command again.


Building the Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you make changes to the documentation,
you can locally re-create the HTML pages using Sphinx_
(which will be automatically installed as part of the development dependencies).
From the main ``jackclient-python`` directory, run::

   uv run sphinx-build doc _build

The generated files will be available in the directory ``_build/``.

.. _Sphinx: https://www.sphinx-doc.org/

While working on the documentation, it might be helpful to re-run Sphinx
whenever something changes.  This can be done with::

    uv run --with sphinx-autobuild sphinx-autobuild doc _build

Running the Tests
^^^^^^^^^^^^^^^^^

There are no proper tests (yet?), but the code examples in the documentation
can be verified with pytest_ (which is also part of the development dependencies).
You can run the (rudimentary) tests with::

   uv run python -m pytest

.. _pytest: https://pytest.org/


Editable Installation
^^^^^^^^^^^^^^^^^^^^^

If you want to work in a different directory on your own files,
but using the latest development version (or a custom branch) of
the ``jack`` module, you can switch to a directory of your choice
and enter this::

   uv init --bare
   uv add --editable --no-workspace path/to/your/jackclient-python/repo

You can install further packages with ``uv add`` and then run
whatever you need with ``uv run``.
