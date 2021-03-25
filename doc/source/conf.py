# -*- coding: utf-8 -*-
# pylint: skip-file
# QA-LeTP documentation build configuration file
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../../legato"))
sys.path.insert(0, os.path.abspath("../../legato/basics"))
sys.path.insert(0, os.path.abspath("../../legato/basics/develop"))
sys.path.insert(0, os.path.abspath("../../legato/basics/sampleApps"))
sys.path.insert(0, os.path.abspath("../../legato/basics/tools"))
sys.path.insert(0, os.path.abspath("../../legato/c-runtime/"))
sys.path.insert(0, os.path.abspath("../../legato/security/"))
sys.path.insert(0, os.path.abspath("../../legato/services/"))


project = 'Qa-LeTP'
copyright = '2021, Sierra Wireless'
author = 'Sierra Wireless'

# The short X.Y version.
version = u"QA_LeTP_version"
# The full version, including alpha/beta/rc tags.
release = u"QA_LeTP_release"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# If true, show .rst source code at the bottom of the generated html page.

html_show_sourcelink = False

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_theme_options = {"page_width": "auto"}