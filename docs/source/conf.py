# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pytropicsquare'
copyright = '2025, Petr Kracik'
author = 'Petr Kracik'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.intersphinx',
    'myst_parser',
]

# Napoleon settings for parsing Google and NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

# Type hints settings
autodoc_typehints = 'description'  # Show type hints in parameter descriptions
autodoc_type_aliases = {
    'L1Transport': 'tropicsquare.transports.L1Transport',
}
python_use_unqualified_type_names = True
autodoc_preserve_defaults = True  # Preserve hex literals like 0xFFFFFFFF instead of converting to decimal

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = False

# Mock imports for MicroPython modules (not available in CPython) and platform-specific modules
autodoc_mock_imports = ['machine', 'micropython', 'utime', 'ubinascii', 'ucryptolib']

# Intersphinx mapping for cross-references to external documentation
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'cryptography': ('https://cryptography.io/en/latest/', None),
}

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Try to use ReadTheDocs theme, fallback to pyramid/classic if not available
try:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_options = {
        'navigation_depth': 5,
        'collapse_navigation': False,
        'sticky_navigation': True,
        'includehidden': True,
        'titles_only': False,
        'prev_next_buttons_location': 'both',
    }
except ImportError:
    html_theme = 'pyramid'  # Better fallback theme - clean and modern

html_static_path = ['_static']
html_title = 'PyTropicSquare Documentation'
html_short_title = 'pytropicsquare'

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",      # ::: fence syntax
    "deflist",          # Definition lists
    "tasklist",         # Task lists [ ]
    "linkify",          # Auto-link URLs
]
myst_heading_anchors = 3  # Generate anchors for h1-h3
