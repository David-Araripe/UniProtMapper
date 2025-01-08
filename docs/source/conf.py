# Configuration file for the Sphinx documentation builder.

import os
import sys
import shutil

sys.path.insert(0, os.path.abspath('../../src'))

# Copy the CSV file to the docs directory
csv_source = '../../src/UniProtMapper/resources/uniprot_return_fields.csv'
csv_dest = os.path.join(os.path.dirname(__file__), '_static')
if not os.path.exists(csv_dest):
    os.makedirs(csv_dest)
shutil.copy2(csv_source, os.path.join(csv_dest, 'uniprot_return_fields.csv'))

# Project information
project = 'UniProtMapper'
copyright = '2025, David Araripe'
author = 'David Araripe'

# The full version, including alpha/beta/rc tags
release = '0.1.0'

# Add any Sphinx extension module names here
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

# Add any paths that contain templates here
templates_path = ['_templates']

# List of patterns to exclude
exclude_patterns = []

# The theme to use for HTML and HTML Help pages
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files
html_static_path = ['_static']

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}