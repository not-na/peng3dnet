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
    def __init__(self,reg,peer,obj=None):
        self.reg = reg
        self.peer = peer
        self.obj = obj
    def _receive(self,msg,cid=None):
        self.receive(msg,cid)
    def _send(self,msg,cid=None):
        self.send(msg,cid)
    def receive(self,msg,cid=None):
        pass
    def send(self,msg,cid=None):
        pass

class SmartPacket(Packet):
    state = STATE_ACTIVE
    side = None
    min_sslsec_level = SSLSEC_NONE
    mode = None
    conntype = None
    invalid_action = "ignore"
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
            raise errors.InvalidSmartPacketAction("Invalid action '%s', ignored packet"%self.invalid_action)
        
        return False
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

class PrintPacket(Packet):
    def receive(self,msg,cid=None):
        if cid is None:
            print("[CLIENT] Received message %s"%msg)
        else:
            print("[SERVER] Received message from %s: %s"%(cid,msg))
