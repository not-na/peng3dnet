#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_util.py
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

import pytest

import peng3dnet

def test_parse_hostname():
    assert peng3dnet.util.parse_address("localhost",80)==("localhost",80)
    assert peng3dnet.util.parse_address("localhost:80")==("localhost",80)
    
    assert peng3dnet.util.parse_address("google.com",80)==("google.com",80)
    assert peng3dnet.util.parse_address("google.com:80")==("google.com",80)

def test_parse_ipv4():
    assert peng3dnet.util.parse_address("127.0.0.1")==("127.0.0.1",8080)
    assert peng3dnet.util.parse_address("127.0.0.1:80")==("127.0.0.1",80)

def test_parse_error_port():
    with pytest.raises(peng3dnet.errors.InvalidPortError):
        peng3dnet.util.parse_address("localhost:abc")
    with pytest.raises(peng3dnet.errors.InvalidPortError):
        peng3dnet.util.parse_address("localhost","abc")
    
    with pytest.raises(peng3dnet.errors.InvalidPortError):
        peng3dnet.util.parse_address("localhost:-1")
    with pytest.raises(peng3dnet.errors.InvalidPortError):
        peng3dnet.util.parse_address("localhost",-1)
    
    with pytest.raises(peng3dnet.errors.InvalidPortError):
        peng3dnet.util.parse_address("localhost:65536")
    with pytest.raises(peng3dnet.errors.InvalidPortError):
        peng3dnet.util.parse_address("localhost",65536)

def test_parse_error_ipv6():
    with pytest.raises(peng3dnet.errors.UnsupportedAddressError):
        peng3dnet.util.parse_address("[1234:1234:1234:1234:1234]:80")
