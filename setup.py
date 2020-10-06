#!/usr/bin/env python

import sys

import setuptools

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

if __name__ == "__main__":
    # This check and everything above must remain compatible with Python 2.7.
    if CURRENT_PYTHON < REQUIRED_PYTHON:
        sys.stderr.write(
            """
    ==========================
    Unsupported Python version
    ==========================
    This version of DRF Integrations Framework requires Python {}.{}, but you're trying
    to install it on Python {}.{}.
    This may be because you are using a version of pip that doesn't
    understand the python_requires classifier. Make sure you
    have pip >= 9.0 and setuptools >= 24.2, then try again.
    This will install the latest version of DRF Integrations Framework which works on
    your version of Python.
    """.format(
                *(REQUIRED_PYTHON + CURRENT_PYTHON)
            )
        )
        sys.exit(1)

    setuptools.setup()
