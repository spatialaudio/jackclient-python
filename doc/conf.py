# Configuration file for Sphinx,
# see https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os
from subprocess import check_output

sys.path.insert(0, os.path.abspath('../src'))
sys.path.insert(0, os.path.abspath('.'))

# Fake import to avoid actually loading CFFI and the JACK library
import fake__jack
sys.modules['_jack'] = sys.modules['fake__jack']


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '1.3'  # for sphinx.ext.napoleon

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  # support for NumPy-style docstrings
    'sphinx_last_updated_by_git',
]

autoclass_content = 'init'
autodoc_member_order = 'bysource'

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = False
napoleon_use_rtype = False

authors = 'Matthias Geier'
project = 'JACK Audio Connection Kit (JACK) Client for Python'
copyright = '2020, ' + authors

nitpicky = True

try:
    release = check_output(['git', 'describe', '--tags', '--always'])
    release = release.decode().strip()
except Exception:
    release = '<unknown>'

try:
    today = check_output(['git', 'show', '-s', '--format=%ad', '--date=short'])
    today = today.decode().strip()
except Exception:
    today = '<unknown date>'

default_role = 'any'


# -- Options for HTML output ----------------------------------------------

html_theme = 'insipid'

html_title = 'JACK Client for Python, version ' + release

html_domain_indices = False

html_show_copyright = False

html_add_permalinks = '\N{SECTION SIGN}'

html_copy_source = False

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
'papersize': 'a4paper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',

'printindex': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [('index', 'JACK-Client.tex', project, authors, 'howto')]

latex_show_urls = 'footnote'

latex_domain_indices = False


# -- Options for epub output ----------------------------------------------

epub_author = authors

epub_use_index = False
