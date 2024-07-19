# -*- coding: utf-8 -*-
"""module to get the correct version information from setuptols_scm generated file"""
from pathlib import Path


def get_version():
    if (Path(__file__).parent / "_version.py").exists():
        from ._version import __version__  # noqa F401
    else:
        __version__ = "1.1.2"
    return __version__
