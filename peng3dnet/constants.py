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
"""
This module is designed to be imported via ``from peng3dnet.constants import *`` without any side-effects.
"""

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
# Equals roughly 4.3 Gigabytes
MAX_PACKETLENGTH = 2**32-1
"""
Constant equal to the maximum packet length representable by the length prefix in bytes.

Currently equals roughly 4.3GB or ``2**32-1`` Bytes.
"""

# Length
STRUCT_FORMAT_LENGTH32 = "!I"
"""
Format of the struct used for the length prefix.

This struct should be able to store a single integer value.

Note that changing this format string will break compatibility with non-modified peers.

For performance reasons, :py:data:`peng3dnet.net.STRUCT_LENGTH32` should be used during runtime instead.
"""
# Packet number, compressed
STRUCT_FORMAT_HEADER = "!IH"
"""
Format of the struct used for the packet header.

This struct should be able to store a packet id encoded as an integer and a bitfield containing flags.

Note that changing this format string will break compatibility with non-modified peers.

For performance reasons, :py:data:`peng3dnet.net.STRUCT_HEADER` should be used during runtime instead.
"""

STATE_INIT = 0
"""
Default connection state of every new connection.
"""
STATE_HANDSHAKE_WAIT1 = 1
"""
Connection state symbolizing the peer has to wait until its peer sends the required packet.

This connection state is part of the internal handshake and should not be used manually.
"""
STATE_HANDSHAKE_WAIT2 = 2
"""
Currently unused connection state.
"""
STATE_WAITTYPE = 3
"""
Active connection state if the server is waiting for the client to send the connection type.

This connection state is part of the internal handshake and should not be used manually.
"""
STATE_HELLOWAIT = 4
"""
Connection state used by the client to wait for the server to send a :py:class:`~peng3dnet.packet.internal.HelloPacket`\ .

This connection state is part of the internal handshake and should not be used manually.
"""
STATE_ACTIVE = 64
"""
Generic state indicating an active connection and successful handshake.
"""
STATE_LOGGEDIN = 65
"""
Generic state indicating an active connection and successful authentication.
"""
STATE_CLOSED = 128
"""
Internal state indicating a closed connection that may be removed completely.
"""

MODE_NOTSET = 0
"""
Placeholder mode used to indicate that the mode has not yet been set.
"""
MODE_CLOSED = 1
"""
Internal mode used to indicate that the connection is not active.
"""
MODE_PING = 2
"""
Old internal mode used to indicate that a ping request is being made.
"""
MODE_PLAY = 3
"""
Generic mode used to indicate that the connection is in play mode.

The exact definition of this mode is up to the application.
"""
MODE_CHAT = 4
"""
Generic mode used to indicate that the connection is in chat mode.
"""

CONNTYPE_NOTSET = "_notset"
"""
Placeholder connection type.

Note that this connection type will cause errors if used, use :py:data:`CONNTYPE_CLASSIC` instead.
"""
CONNTYPE_CLASSIC = "classic"
"""
Classic connection type.

.. seealso::
   See :py:class:`peng3dnet.conntypes.ClassicConnectionType` for more information.
"""
CONNTYPE_PING = "ping"
"""
Ping request connection type.

.. seealso:
   See :py:mod:`peng3dnet.ext.ping` for more information.
"""

FLAG_COMPRESSED =       1 << 0
"""
Flag bit set if the packet is compressed.
"""
FLAG_ENCRYPTED_AES =    1 << 1
"""
Flag bit set if the packet is AES-Encrypted.

Note that this flag is currently not implemented.
"""

SIDE_CLIENT = 0
"""
Constant used to indicate the client side of the server-client relationship.
"""
SIDE_SERVER = 1
"""
Constant used to indicate the server side of the server-client relationship.
"""

SSLSEC_NONE = 0
"""
SSL Security level indicating that there is no SSL tunneling active.

Default SSL Security level.
"""
SSLSEC_WRAPPED = 1
"""
SSL Security level indicating that the socket has been wrapped in a SSLSocket.

Note that this usually isn't more secure compared to :py:data:`SSLSEC_NONE`\ .
"""
SSLSEC_ENCRYPTED = 2
"""
SSL Security level indicating that the SSL Tunnel uses encryption.

Only encryption enabled by the default in the standard library module :py:mod:`ssl` is regarded as secure.
"""
SSLSEC_SERVERAUTH = 3
"""
SSL Security level indicating that the server certificate is authentic and valid.

This includes hostname verification.
"""
SSLSEC_BOTHAUTH = 4
"""
SSL Security level indicating that both server and client certificate are authentic and valid.

This includes hostname verification.
"""

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
    "net.ssl.cafile":None,
    "net.ssl.server.force_verify":True, # corresponds to verify_mode
    "net.ssl.server.certfile":None,
    "net.ssl.server.keyfile":None,
    "net.ssl.client.check_hostname":False,
    "net.ssl.client.force_verify":False,
    
    "net.events.enable":"auto",
    
    "net.debug.print.recv":False,
    "net.debug.print.send":False,
    "net.debug.print.connect":False,
    "net.debug.print.close":False,
    
    "net.registry.autosync":True,
    "net.registry.missingpacketaction":"closeconnection",
    }
"""
Default configuration values.

This dictionary is used to look up default config values.

.. seealso::
   See :doc:`../configoption` for a list of all config options.
"""
