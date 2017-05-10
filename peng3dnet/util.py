#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  util.py
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

from . import errors

def parse_address(addr,default_port=8080):
    addr = str(addr)
    addrs = addr.split(":")
    if len(addrs)==1:
        addr = addrs[0]
        port = default_port
    elif len(addrs)==2:
        addr = addrs[0]
        try:
            port = int(addrs[1])
        except Exception:
            raise errors.InvalidPortError("Port %s is not an integer"%addrs[1])
    else:
        raise errors.UnsupportedAddressError("Address appears to be an IPv6 address, currently not supported")
    if not isinstance(port,int):
        raise errors.InvalidPortError("Port must be an integer")
    elif port<0:
        raise errors.InvalidPortError("Port may not be less than zero")
    elif port>65535:
        raise errors.InvalidPortError("Port may not be higher than 65535")
    # TODO: add address validation
    return addr,port

def normalize_addr_socketstyle(addr,default_port=8080):
    if len(addr)==2:
        return addr
    else:
        return parse_address(addr,default_port)

def normalize_addr_formatted(addr):
    raise NotImplementedError("not yet implemented")
