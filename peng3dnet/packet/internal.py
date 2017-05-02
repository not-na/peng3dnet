#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  internal.py
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
    "HandshakePacket", "HandshakeAcceptPacket",
    "CloseConnectionPacket",
    ]

from . import Packet, SmartPacket
from ..constants import *
from .. import version

class HandshakePacket(SmartPacket):
    state = STATE_INIT
    side = SIDE_CLIENT
    def receive(self,msg,cid=None):
        if msg["version"]!=version.VERSION:
            pass # for now...
        if msg["protoversion"]!=version.PROTOVERSION:
            self.peer.close_connection(cid,"protoversionmismatch")
            return
        
        # Sync registry
        if msg["registry"].keys()!=self.peer.registry.reg_int_str._inv.keys():
            self.peer.close_connection(cid,"packetregmismatch")
            return
        
        for name,pid in msg["registry"].items():
            obj = self.peer.registry.getObj(name)
            self.peer.registry.reg_int_str._inv[name]=pid
            self.peer.registry.reg_int_obj._inv[obj]=pid
        
        self.peer.send_message("peng3dnet:internal.handshake.accept",{"success":True})
        self.peer.on_handshake_complete()

class HandshakeAcceptPacket(SmartPacket):
    state = STATE_HANDSHAKE_WAIT1
    side = SIDE_SERVER
    def receive(self,msg,cid):
        if msg["success"]:
            self.peer.clients[cid].on_handshake_complete()

class CloseConnectionPacket(Packet):
    def receive(self,msg,cid=None):
        if isinstance(msg,dict):
            reason = msg.get("reason",None)
        else:
            reason = None
        
        if cid is None:
            # On the client
            self.peer.close(reason=reason)
        else:
            # On the server
            client = self.peer.clients[cid]
            client.close(reason)
            # Everything else is handled by the class
