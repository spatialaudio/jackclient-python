Contributing
------------

If you find bugs, errors, omissions or other things that need improvement,
please create an issue or a pull request at
https://github.com/spatialaudio/jackclient-python.
Contributions are always welcome!

Instead of pip-installing the latest release from PyPI, you should get the
newest development version from Github_::

   git clone https://github.com/spatialaudio/jackclient-python.git
   cd jackclient-python
   python3 -m pip install --user -e .

... where ``-e`` stands for ``--editable``.
This way, your installation always stays up-to-date, even if you pull new
changes from the Github repository.

.. _Github: https://github.com/spatialaudio/jackclient-python/

.. note::

   Whenever the file ``jack_build.py`` changes (either because you edited it or
   it was updated by pulling from Github or switching branches), you have to
   run the last command again.

If you make changes to the documentation, you can locally re-create the HTML
pages using Sphinx_.
You can install it and a few other necessary packages with::

   python3 -m pip install -r doc/requirements.txt --user

To create the HTML pages, use::

   python3 setup.py build_sphinx

The generated files will be available in the directory ``build/sphinx/html/``.

.. _Sphinx: http://sphinx-doc.org/

There are no proper tests (yet?), but the code examples from the README file
can be verified with pytest_.
If you haven't installed it already, you can install it with::

   python3 -m pip install pytest ---user

As soon as pytest_ is installed, you can run the (rudimentary) tests with::

   python3 -m pytest

.. _pytest: https://pytest.org/
