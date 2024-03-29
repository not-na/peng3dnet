# `peng3dnet` - Networking Library for `peng3d`

[![Documentation Status](https://readthedocs.org/projects/peng3dnet/badge/?version=latest)](https://peng3dnet.readthedocs.io/en/latest/?badge=latest)

`peng3dnet` is a TCP-Based networking Library designed for use with [peng3d](https://github.com/not-na/peng3d).

It uses Length-Prefixing to cut the raw TCP Stream into packets, which are usually [MessagePack](http://msgpack.org/)\-encoded Python objects.

`peng3dnet` has been tested and is developed under Python 3.7, however it should work
with newer versions as well.

## Documentation

The current documentation is available [here](https://peng3dnet.readthedocs.io) on ReadTheDocs.

The Sphinx-based source for the documentation is available in the `docs/` subdirectory.
Documentation for specific methods and classes is usually found in the docstring of the method/class.

Some basic examples can also be found in the `examples/` directory of the main repository.

## Requirements

Currently, `peng3dnet` requires only two modules:
- [bidict](https://github.com/jab/bidict), as PyPI package `bidict`
- [msgpack](https://github.com/msgpack/msgpack-python) or [u-msgpack-python](https://github.com/vsergeev/u-msgpack-python), each available under the same name on PyPI

Note that `msgpack` may be faster, since it has a C-extension.
In cases where C-extensions cannot be used, `u-msgpack-python` can be used, since it should work on all platforms and is written in pure Python.

## Installation via `pip`

If possible, this method of installation is to be preferred.

Installation via `pip` is simple:

`pip install peng3dnet`

Note that on some systems it may be necessary to use `sudo pip install peng3dnet` if the above command fails.

When sharing requirements, a `requirements.txt` file is recommended. See the official pip
documentation for details.

## Installation via `setup.py`

If possible, use `pip` instead.

Installation via `setup.py`:

`python setup.py install`

Note that using this method requires manually installing the dependencies and downloading of the repository.
It may also be necessary to use `sudo python setup.py install` if the above command fails.
