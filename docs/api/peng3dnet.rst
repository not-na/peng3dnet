
``peng3dnet`` - Peng3dnet Main Package
======================================

.. py:module:: peng3dnet
   :synopsis: Peng3dnet Main Package

This package represents the root package of the ``peng3dnet`` networking library.

Most classes defined in submodules are also available at the package level, e.g.
:py:class:`peng3dnet.net.Server()` will also be available as :py:class:`peng3dnet.Server()`\ .

``*``\ -importing submodules and packages should generally be safe, as all
modules use the ``__all__`` variable to explicitly define their exported classes.

.. toctree::
   :maxdepth: 1
   
   peng3dnet.net
   peng3dnet.constants
   packet/index
   packet/internal
   peng3dnet.registry
   peng3dnet.version
