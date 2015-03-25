Contributing
------------

If you find bugs, errors, omissions or other things that need improvement,
please create an issue or a pull request at
http://github.com/spatialaudio/jackclient-python.
Contributions are always welcome!

If you make changes to the documentation, you can re-create the HTML pages
using Sphinx_.

.. _Sphinx: http://sphinx-doc.org/

You can install it and a few other necessary packages with::

   pip install -r doc/requirements.txt --user

To create the HTML pages, use::

   python setup.py build_sphinx

The generated files will be available in the directory ``build/sphinx/html/``.

There are no proper tests (yet?), but the code examples from the README file
can be verified by::

   python setup.py test

This uses py.test_; if you haven't installed it already, it will be downloaded
and installed for you.

.. _py.test: http://pytest.org/
