Introduction
============


.. image:: https://readthedocs.org/projects/micropython-pca9685/badge/?version=latest
    :target: https://micropython-pca9685.readthedocs.io/en/latest/
    :alt: Documentation Status


.. image:: https://img.shields.io/badge/micropython-Ok-purple.svg
    :target: https://micropython.org
    :alt: micropython

.. image:: https://img.shields.io/pypi/v/micropython-pca9685.svg
    :alt: latest version on PyPI
    :target: https://pypi.python.org/pypi/micropython-pca9685

.. image:: https://static.pepy.tech/personalized-badge/micropython-pca9685?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Pypi%20Downloads
    :alt: Total PyPI downloads
    :target: https://pepy.tech/project/micropython-pca9685

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

MicroPython Driver for the PCA9685
This include the a servo helper. The servo helper is taken from the
adafruit_circuitpython_motor library and adapted to MicroPython.

If you are interested in a great MicroPython PCA9685 library take a look at
https://github.com/pappavis/micropython-pca9685



Installing with mip
====================
To install using mpremote

.. code-block:: shell

    mpremote mip install github:jposada202020/MicroPython_PCA9685

To install directly using a WIFI capable board

.. code-block:: shell

    mip install github:jposada202020/MicroPython_PCA9685


Installing Library Examples
============================

If you want to install library examples:

.. code-block:: shell

    mpremote mip install github:jposada202020/MicroPython_PCA9685/examples.json

To install directly using a WIFI capable board

.. code-block:: shell

    mip install github:jposada202020/MicroPython_PCA9685/examples.json


Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/micropython-pca9685/>`_.
To install for current user:

.. code-block:: shell

    pip3 install micropython-pca9685

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install micropython-pca9685

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install micropython-pca9685


Usage Example
=============

Take a look at the examples directory

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://micropython-pca9685.readthedocs.io/en/latest/>`_.
