#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  errors.py
#  
#  Copyright 2017 notna <notna@apparat.org>
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
"""
This module contains the various exception classes used by peng3dnet.

Most methods and functions that use these exceptions will have a link to the appropriate exception in their documentation.
"""

__all__ = [
    "InvalidAddressError","InvalidPortError","InvalidHostError",
    "UnsupportedAddressError",
    "InvalidSmartPacketActionError",
    "TimedOutError","FailedPingError",
    "RegistryError","AlreadyRegisteredError",
    ]

class InvalidAddressError(ValueError):
    """
    Indicates that a given address is not valid and thus cannot be used.
    """
    pass

class InvalidPortError(InvalidAddressError):
    """
    Indicates that the port supplied or parsed is not valid.
    """
    pass
class InvalidHostError(InvalidAddressError):
    """
    Indicates that the host supplied or parsed is not valid or applicable.
    """
    pass

class UnsupportedAddressError(NotImplementedError):
    """
    Indicates that the address supplied is not supported, but may still be valid.
    """
    pass

class InvalidSmartPacketActionError(ValueError):
    """
    Raised if the ``invalid_action`` of a :py:class:`~peng3dnet.packet.SmartPacket` is not valid.
    """
    pass

class TimedOutError(RuntimeError):
    """
    Indicates that some action has timed out, this includes connections, requests and any other applicable action.
    """
    pass
class FailedPingError(TimedOutError):
    """
    Indicates that a ping request has failed, usually due to a timeout.
    """
    pass

class RegistryError(ValueError):
    """
    Indicates that a registry has encountered an error.
    """
    pass

class AlreadyRegisteredError(RegistryError):
    """
    Indicates that the object given has already been registered.
    """
    pass
