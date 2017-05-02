#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  constants.py
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

__all__ = [
    "MAX_PACKETLENGTH",
    "COMPRESS_THRESHOLD","COMPRESS_LEVEL",
    "STRUCT_LENGTH32","STRUCT_HEADER",
    
    "STATE_INIT",
    "STATE_HANDSHAKE_WAIT1","STATE_HANDSHAKE_WAIT2",
    "STATE_ACTIVE","STATE_CLOSED",
    
    "FLAG_COMPRESSED","FLAG_ENCRYPTED_AES",
    
    "SIDE_CLIENT","SIDE_SERVER",
    ]
import struct

# Maximum representable by prefix
# Equals roughly 2.4 Gigabytes
MAX_PACKETLENGTH = 2**32-1

COMPRESS_THRESHOLD = 8*1024
COMPRESS_LEVEL = 6

# Length
STRUCT_LENGTH32 = struct.Struct("!I")
# Packet number, compressed
STRUCT_HEADER = struct.Struct("!IH")

STATE_INIT = 0
STATE_HANDSHAKE_WAIT1 = 1
STATE_HANDSHAKE_WAIT2 = 2
STATE_ACTIVE = 64
STATE_CLOSED = 128

FLAG_COMPRESSED =       1 << 0
FLAG_ENCRYPTED_AES =    1 << 1

SIDE_CLIENT = 0
SIDE_SERVER = 1
