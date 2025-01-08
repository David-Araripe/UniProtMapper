# Configuration file for the Sphinx documentation builder.
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath('../../src'))

# Project information
project = 'UniProtMapper'
copyright = '2025, David Araripe'
author = 'David Araripe'

# The full version, including alpha/beta/rc tags
release = '0.1.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
]

# Autodoc configurations
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "special-members": False,
    "inherited-members": True,
    "show-inheritance": True
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_ivar = True

# Paths and patterns
templates_path = ['_templates']
html_static_path = ['_static']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Theme configuration
html_theme = 'sphinx_rtd_theme'
html_show_sourcelink = False

# Copy data files if needed
csv_source = Path('../../src/UniProtMapper/resources/uniprot_return_fields.csv')
csv_dest = Path('_static')
csv_dest.mkdir(exist_ok=True)
if csv_source.exists():
    import shutil
    shutil.copy2(csv_source, csv_dest / 'uniprot_return_fields.csv')

# Intersphinx mapping
intersphinx_mapping = {'python': ('https://docs.python.org/3.9', None)}