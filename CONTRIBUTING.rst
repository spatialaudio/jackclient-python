Contributing
------------

If you find bugs, errors, omissions or other things that need improvement,
please create an issue or a pull request at
http://github.com/spatialaudio/jackclient-python.
Contributions are always welcome!

Instead of pip-installing the latest release from PyPI, you should get the newest
development version from Github_::

   git clone https://github.com/spatialaudio/jackclient-python.git
   cd jackclient-python
   python setup.py develop --user

.. _Github: http://github.com/spatialaudio/jackclient-python/

This way, your installation always stays up-to-date, even if you pull new
changes from the Github repository.

If you prefer, you can also replace the last command with::

   pip install --user -e .

... where ``-e`` stands for ``--editable``.

If you make changes to the documentation, you can re-create the HTML pages
using Sphinx_.
You can install it and a few other necessary packages with::

   pip install -r doc/requirements.txt --user

To create the HTML pages, use::

   python setup.py build_sphinx

The generated files will be available in the directory ``build/sphinx/html/``.

.. _Sphinx: http://sphinx-doc.org/

There are no proper tests (yet?), but the code examples from the README file
can be verified by::

   python setup.py test

This uses py.test_; if you haven't installed it already, it will be downloaded
and installed for you.

.. _py.test: http://pytest.org/
