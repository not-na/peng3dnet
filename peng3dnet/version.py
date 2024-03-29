#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  version.py
#  
#  Copyright 2017-2022 notna <notna@apparat.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


__all__ = ["VERSION","RELEASE","PROTOVERSION"]

VERSION = "0.2.0"
"""
Full version number of this package.

Used to display the version in the title of the documentation and in ``setup.py``\\ .

.. seealso::
   
   See `Semantic Versioning <http://semver.org>`_ for more information on the scheme used by this application.
"""

RELEASE = "0.2.0"
"""
Full version number of this package without trailing meta-data.

See :py:data:`VERSION` for more information.
"""

PROTOVERSION = 2
"""
Version of the protocol used internally.

This value is shared during the handshake of a connection.

Two versions of this library that do not share the same protocol versions are probably not compatible.
"""
