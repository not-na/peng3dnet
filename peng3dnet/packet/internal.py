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
    "HelloPacket","SetTypePacket",
    "HandshakePacket", "HandshakeAcceptPacket",
    "CloseConnectionPacket",
    ]

from . import Packet, SmartPacket
from ..constants import *
from .. import version

class HelloPacket(SmartPacket):
    state = STATE_HELLOWAIT
    side = SIDE_CLIENT
    conntype = CONNTYPE_NOTSET
    def receive(self,msg,cid=None):
        if msg["version"]!=version.VERSION:
            pass # for now...
        if msg["protoversion"]!=version.PROTOVERSION:
            self.peer.close_connection(cid,"protoversionmismatch")
            return
        
        if self.peer.cfg["net.debug.print.connect"]:
            print("HELLO")
        
        self.peer.send_message("peng3dnet:internal.settype",{"conntype":self.peer.target_conntype})
        
        self.peer.remote_state = STATE_WAITTYPE
        
        self.peer.conntypes[self.peer.target_conntype].init(cid)
    def send(self,msg,cid=None):
        self.peer.clients[cid].state = STATE_WAITTYPE
        if self.peer.cfg["net.debug.print.connect"]:
            print("HELLO %s"%cid)

class SetTypePacket(SmartPacket):
    state = STATE_WAITTYPE
    side = SIDE_SERVER
    def receive(self,msg,cid=None):
        t = msg.get("conntype","classic")
        
        if t not in self.peer.conntypes:
            self.peer.close_connection("unknownconntype",cid)
            return
        
        self.peer.clients[cid].conntype = t
        self.peer.conntypes[t].init(cid)

class HandshakePacket(SmartPacket):
    state = STATE_HANDSHAKE_WAIT1
    side = SIDE_CLIENT
    invalid_action = "close"
    def receive(self,msg,cid=None):
        if msg["version"]!=version.VERSION:
            pass # for now...
        if msg["protoversion"]!=version.PROTOVERSION:
            self.peer.close_connection(cid,"protoversionmismatch")
            return
        
        if self.peer.cfg["net.registry.autosync"]:
            # Sync registry
            if msg["registry"].keys()!=self.peer.registry.reg_int_str._inv.keys():
                if self.peer.cfg["net.registry.missingpacketaction"]=="closeconnection":
                    self.peer.close_connection(cid,"packetregmismatch")
                    return
                elif self.peer.cfg["net.registry.missingpacketaction"]=="ignore":
                    pass
            
            for name,pid in msg["registry"].items():
                if name in self.peer.registry.reg_int_str._inv:
                    obj = self.peer.registry.getObj(name)
                    opid = self.peer.registry.getInt(name)
                    
                    del self.peer.registry.reg_int_str[opid]
                    del self.peer.registry.reg_int_obj[opid]
                    
                    self.peer.registry.reg_int_str[pid]=name
                    self.peer.registry.reg_int_obj[pid]=obj
        
        self.peer.send_message("peng3dnet:internal.handshake.accept",{"success":True})
        self.peer.on_handshake_complete()
        with self.peer._connected_condition:
            self.peer._connected_condition.notify_all()

class HandshakeAcceptPacket(SmartPacket):
    state = STATE_HANDSHAKE_WAIT1
    side = SIDE_SERVER
    invalid_action = "close"
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
