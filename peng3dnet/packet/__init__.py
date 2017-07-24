#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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
    "Packet", "SmartPacket",
    "PrintPacket",
    ]

from ..constants import *
from ..errors import *

class Packet(object):
    """
    Class representing a packet type.
    
    ``reg`` is an instance of :py:class:`~peng3dnet.registry.PacketRegistry` shared between all packet types registered with it.
    
    ``peer`` is the peer this packet type belongs to.
    
    .. todo::
       Find out what ``obj`` does... Seems to be an unused artifact from a test.
    """
    def __init__(self,reg,peer,obj=None):
        self.reg = reg
        self.peer = peer
        self.obj = obj
    def _receive(self,msg,cid=None):
        """
        Internal handler called whenever a packet of this type is received.
        
        By default, this method passes its arguments through to :py:meth:`receive()`\ .
        
        May be overridden by subclasses to prevent further processing.
        """
        self.receive(msg,cid)
    def _send(self,msg,cid=None):
        """
        Internal handler called whenever a packet of this type has been sent.
        
        By default, this method passes its arguments through to :py:meth:`send()`\ .
        
        May be overridden by subclasses to prevent further processing.
        """
        self.send(msg,cid)
    def receive(self,msg,cid=None):
        """
        Event handler called when a packet of this type is received.
        
        Note that this method is usually called by :py:meth:`_receive()`\ , which may also decide to silently ignore a packet.
        
        ``msg`` is the fully decoded message or payload, usually a dictionary.
        
        ``cid`` is the ID of the peer that sent the message. If this is ``None``\ , the packet was received on the client side, else it equals the client ID of the client.
        """
        pass
    def send(self,msg,cid=None):
        """
        Event handler called when a packet of this type has been sent.
        
        Note that this method is usually called by :py:meth:`_send()`\ , which may also decide to silently ignore a packet.
        
        ``msg`` is the already encoded message.
        
        ``cid`` is the ID of the peer that should receive the message. If this is ``None``\ , the packet was sent on the client side, else it equals the client ID of the recipient.
        """
        pass

class SmartPacket(Packet):
    """
    Smart packet type allowing for various assertions.
    
    This class is not intended to be used directly, use subclasses and override
    the class attributes for customization.
    
    This class overrides the :py:meth:`_receive` and :py:meth:`_send` methods to
    check that the connection is in a valid state for this packet.
    """
    state = STATE_ACTIVE
    """
    Specifies the connection state required for the packet, both on send and receive.
    
    If the state does not match exactly, the action specified in
    :py:attr:`invalid_action` is executed.
    """
    side = None
    """
    Specifies the side of the connection this packet can be received.
    
    If this is ``None``\ , it can be received on both ends of a connection.
    If this is :py:data:`~peng3dnet.constants.SIDE_SERVER` or
    :py:data:`~peng3dnet.constants.SIDE_CLIENT`\ , it can be received on the
    server or client side, respectively.
    
    Note that packets that can only be received on the client side can only be
    sent from the server side, and vice versa.
    
    In the case that this condition does not match, the action specified in
    :py:attr:`invalid_action` is executed.
    """
    min_sslsec_level = SSLSEC_NONE
    """
    Declares the minimum level of SSL encryption required for this packet to be sent.
    
    This is not checked on receival of a message, only during sending of the message.
    
    Possible values are any of the :py:data:`~peng3dnet.constants.SSLSEC_*` constants.
    
    If the actual SSL security level is lower than the required level, the action
    specified in :py:attr:`invalid_action` is executed.
    """
    mode = None
    """
    Specifies the connection mode required for this packet to be sent or received.
    
    If this is ``None``\ , this check will be skipped.
    
    Else, if the specified connection mode does not exactly match the actual
    connection mode, the action specified in :py:attr:`invalid_action` is executed.
    """
    conntype = None
    """
    Declares the required connection type for this packet to be sent or retrieved.
    
    If this is ``None``\ , this check will be skipped.
    
    Else, if the specified value does not match the actual value, the action
    specified in :py:attr:`invalid_action` is executed.
    """
    invalid_action = "ignore"
    """
    Specifies what to do if one of the conditions specified is not fulfilled.
    
    Can be either ``ignore`` or ``close``\ .
    A value of ``ignore`` causes this packet to be ignored. Note that due to
    technical reasons, the packet may still be processed by other mechanisms.
    In contrast, a value of ``close`` will cause the connection to be closed with the reason ``smartpacketinvalid``\ .
    
    If an invalid value is used, an :py:exc:`~peng3dnet.errors.InvalidSmartPacketActionError` will be raised and the packet ignored.
    """
    def _receive(self,msg,cid=None):
        if cid is None and (self.side is None or self.side == SIDE_CLIENT):
            # On the client
            if (self.peer.remote_state == self.state
                and (self.mode is None or self.peer.mode==self.mode)
                and (self.conntype is None or self.peer.conntype==self.conntype)
                ):
                self.receive(msg,cid)
                return True
        elif cid is not None and (self.side is None or self.side == SIDE_SERVER):
            # On the server
            if (self.peer.clients[cid].state == self.state
                and (self.mode is None or self.peer.clients[cid].mode==self.mode)
                and (self.conntype is None or self.peer.clients[cid].conntype==self.conntype)
                ):
                self.receive(msg,cid)
                return True
        
        if self.invalid_action=="ignore":
            pass
        elif self.invalid_action=="close":
            # Client should just ignore the cid
            self.peer.close_connection(cid,"smartpacketinvalid")
        else:
            raise errors.InvalidSmartPacketActionError("Invalid action '%s', ignored packet"%self.invalid_action)
        
        return False
    _receive.__noautodoc__ = True
    def _send(self,msg,cid=None):
        if cid is None and (self.side is None or self.side == SIDE_SERVER):
            # On the client
            if (self.peer.remote_state == self.state
                and self.peer.ssl_seclevel>=self.min_sslsec_level
                and (self.mode is None or self.peer.mode==self.mode)
                and (self.conntype is None or self.peer.conntype==self.conntype)
                ):
                self.send(msg,cid)
                return True
        elif cid is not None and (self.side is None or self.side == SIDE_CLIENT):
            # On the server
            if (self.peer.clients[cid].state == self.state
                and self.peer.clients[cid].ssl_seclevel>=self.min_sslsec_level
                and (self.mode is None or self.peer.clients[cid].mode==self.mode)
                and (self.conntype is None or self.peer.clients[cid].conntype==self.conntype)
                ):
                self.send(msg,cid)
                return True
        
        if self.invalid_action=="ignore":
            pass
        elif self.invalid_action=="close":
            # Client should just ignore the cid
            self.peer.close_connection(cid,"smartpacketinvalid")
        else:
            raise errors.InvalidSmartPacketAction("Invalid action '%s', ignored packet"%self.invalid_action)
        
        return False
    _send.__noautodoc__ = True

class PrintPacket(Packet):
    """
    Simple dummy packet class that prints any message it receives.
    
    If a packet is received on the server, the client ID of the client is also printed.
    """
    def receive(self,msg,cid=None):
        if cid is None:
            print("[CLIENT] Received message %s"%msg)
        else:
            print("[SERVER] Received message from %s: %s"%(cid,msg))
    receive.__noautodoc__ = True
