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
    "STRUCT_FORMAT_LENGTH32","STRUCT_FORMAT_HEADER",
    
    "STATE_INIT",
    "STATE_HANDSHAKE_WAIT1","STATE_HANDSHAKE_WAIT2",
    "STATE_WAITTYPE","STATE_HELLOWAIT",
    "STATE_LOGGEDIN",
    "STATE_ACTIVE","STATE_CLOSED",
    
    "MODE_NOTSET","MODE_CLOSED",
    "MODE_PING","MODE_PLAY","MODE_CHAT",
    
    "CONNTYPE_NOTSET","CONNTYPE_CLASSIC","CONNTYPE_PING",
    
    "FLAG_COMPRESSED","FLAG_ENCRYPTED_AES",
    
    "SIDE_CLIENT","SIDE_SERVER",
    
    "SSLSEC_NONE","SSLSEC_WRAPPED","SSLSEC_ENCRYPTED",
    "SSLSEC_SERVERAUTH","SSLSEC_BOTHAUTH",
    
    "DEFAULT_CONFIG"
    ]

# Maximum representable by prefix
# Equals roughly 2.4 Gigabytes
MAX_PACKETLENGTH = 2**32-1

# Length
STRUCT_FORMAT_LENGTH32 = "!I"
# Packet number, compressed
STRUCT_FORMAT_HEADER = "!IH"

STATE_INIT = 0
STATE_HANDSHAKE_WAIT1 = 1
STATE_HANDSHAKE_WAIT2 = 2
STATE_WAITTYPE = 3
STATE_HELLOWAIT = 4
STATE_ACTIVE = 64
STATE_LOGGEDIN = 65
STATE_CLOSED = 128

MODE_NOTSET = 0
MODE_CLOSED = 1
MODE_PING = 2
MODE_PLAY = 3
MODE_CHAT = 4

CONNTYPE_NOTSET = "_notset"
CONNTYPE_CLASSIC = "classic"
CONNTYPE_PING = "ping"

FLAG_COMPRESSED =       1 << 0
FLAG_ENCRYPTED_AES =    1 << 1

SIDE_CLIENT = 0
SIDE_SERVER = 1

SSLSEC_NONE = 0
SSLSEC_WRAPPED = 1
SSLSEC_ENCRYPTED = 2
SSLSEC_SERVERAUTH = 3
SSLSEC_BOTHAUTH = 4

DEFAULT_CONFIG = {
    "net.server.addr":None,
    "net.server.addr.host":"0.0.0.0",
    "net.server.addr.port":8080,
    
    "net.client.addr":None,
    "net.client.addr.host":"localhost",
    "net.client.addr.port":8080,
    
    "net.compress.enabled":True,
    "net.compress.threshold":8*1024, # 8KiB
    "net.compress.level":6,
    
    "net.encrypt.enabled":False,
    # TODO
    
    # Disabled for now, not yet working
    "net.ssl.enabled":False,
    "net.ssl.force":True,
    "net.ssl.server.force_verify":True, # corresponds to verify_mode
    "net.ssl.server.certfile":None,
    "net.ssl.server.keyfile":None,
    "net.ssl.client.check_hostname":True,
    "net.ssl.client.force_verify":False,
    
    "net.events.enable":"auto",
    
    "net.debug.print.recv":False,
    "net.debug.print.send":False,
    "net.debug.print.connect":False,
    "net.debug.print.close":False,
    
    "net.registry.autosync":True,
    "net.registry.missingpacketaction":"closeconnection",
    }
