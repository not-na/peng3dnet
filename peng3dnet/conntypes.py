#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  conntypes.py
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

__all__ = ["ConnectionType","ClassicConnectionType"]

from . import version
from .constants import *

class ConnectionType(object):
    """
    Class representing a Connection Type implementation.
    
    Connection Types are identified by their name, usually a lowercase string.
    
    See :py:class:`~peng3dnet.net.Client()` for how to specify the connection type used.
    
    To use a custom connection type, it must be registered on both server and client via
    :py:meth:`Server.addConnType() <peng3dnet.net.Server.addConnType>` or
    :py:meth:`Client.addConnType() <peng3dnet.net.Client.addConnType>`\ , respectively.
    
    ``peer`` is an instance of either :py:class:`~peng3dnet.net.Client()` or
    :py:class:`~peng3dnet.net.Server()`\ .
    
    Note that a single instance of this class will be shared between all connections
    of the type implemented by this class. Distinguishing single connections is
    possible via the ``cid`` parameter given to most methods. On the client side,
    this parameter will always be ``None``\ .
    """
    def __init__(self,peer):
        self.peer = peer
    def init(self,cid):
        """
        Called when the :py:class:`~peng3dnet.packet.internal.SetTypePacket()`
        is received on the server side, or sent on the client side.
        
        Detecting which side of the connection is managed can be done by checking
        the ``cid`` parameter, if it is ``None``\ , the client side is represented,
        else it represents the ID of the connected client.
        """
        pass
    def receive(self,msg,pid,flags,cid):
        """
        Called whenever a packet is received via connection of the type represented by this class.
        
        ``msg`` is the already decoded message or payload.
        
        ``pid`` is the ID of the packet type.
        
        ``flags`` is the flags portion of the header, containing a bitfield with various internal flags.
        
        ``cid`` is the ID of the connected peer, if it is ``None``\ , the peer is a server.
        
        If the return value of this method equals to ``True``\ , further processing of the packet will be prevented.
        """
        # Return value of true would cause halting of processing
        return False
    def send(self,data,pid,cid):
        """
        Called whenever a packet has been sent via a connection of the type represented by this class.
        
        ``data`` is the fully encoded data that has been sent.
        
        ``pid`` is the packet type, as received by either
        :py:meth:`Server.send_message() <peng3dnet.net.Server.send_message>` or
        :py:meth:`Client.send_message() <peng3dnet.net.Client.send_message>`\ .
        
        ``cid`` is the ID of the connected peer, it if is ``None``\ , the peer is a server.
        
        If the return value of this method equals to ``True``\ , no further event handlers will be called.
        """
        # Return value of true would cause halting of processing
        return False

class ClassicConnectionType(ConnectionType):
    """
    Classic Connection Type representing a typical connection.
    
    Currently adds no further processing to packets and starts a handshake by sending a :py:class:`~peng3dnet.packet.internal.HandshakePacket()` from the server to the client.
    
    The handshake allows the client to copy the registry of the server, preventing bugs with mismatching packet IDs.
    """
    def init(self,cid):
        if cid is not None:
            self.peer.clients[cid].state = STATE_HANDSHAKE_WAIT1
            self.peer.send_message("peng3dnet:internal.handshake",{"version":version.VERSION,"protoversion":version.PROTOVERSION,"registry":dict(self.peer.registry.reg_int_str._inv)},cid)
        elif cid is None:
            self.peer.remote_state = STATE_HANDSHAKE_WAIT1
    init.__noautodoc__ = True
