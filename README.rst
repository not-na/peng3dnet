``peng3dnet`` - Networking Library for ``peng3d``
=================================================

.. image:: https://readthedocs.org/projects/peng3dnet/badge/?version=latest
   :target: http://peng3dnet.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://circleci.com/gh/not-na/peng3dnet.svg?style=svg
    :target: https://circleci.com/gh/not-na/peng3dnet

.. image:: https://img.shields.io/pypi/dm/peng3dnet.svg
   :target: https://pypi.python.org/pypi/peng3dnet


``peng3dnet`` is a TCP-Based networking Library designed for use with `peng3d <https://github.com/not-na/peng3d>`_\ .

It uses Length-Prefixing to cut the raw TCP Stream into packets, which are usually `MessagePack <http://msgpack.org/>`_\ -encoded Python objects.

``peng3dnet`` has been tested and is developed under Python 3.5, however it should work with newer versions as well.
Python 2.x support is currently not planned, but may be possible by rewriting small parts of the code.

Documentation
-------------

The current documentation is available `here <https://peng3dnet.readthedocs.io>`_ on ReadTheDocs.

The Sphinx-based source for the documentation is available in the ``docs/`` subdirectory.
Documentation for specific methods and classes is usually found in the docstring of the method/class.

Requirements
------------

Currently, ``peng3dnet`` requires only two modules:
- `bidict <https://github.com/jab/bidict>`_\ , as PyPI package ``bidict``
- `msgpack-python <https://github.com/msgpack/msgpack-python>`_ or `u-msgpack-python <https://github.com/vsergeev/u-msgpack-python>`_\ , available under the same name on PyPI

Note that ``msgpack-python`` may be faster, since it has a C-extension.
In cases where C-extensions cannot be used, ``u-msgpack-python`` can be used, since it should work on all platforms and is written in pure Python.

Installation via ``pip``
------------------------

If possible, this method of installation is to be preferred.

Installation via ``pip`` is simple::
    
    pip install peng3dnet

Note that on some systems it may be necessary to use ``sudo pip install peng3dnet`` if the above command fails.

Installation via ``setup.py``
-----------------------------

If possible, use ``pip`` instead.

Installation via ``setup.py``\ ::
    
    python setup.py install

Note that using this method requires manually installing the dependencies and downloading of the repository.
It may also be necessary to use ``sudo python setup.py install`` if the above command fails.

