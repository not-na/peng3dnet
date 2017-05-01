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

from .. import net

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
    state = net.STATE_ACTIVE
    side = None
    def _receive(self,msg,cid=None):
        if cid is None and (self.side is None or self.side == net.SIDE_CLIENT):
            if self.peer.remote_state == self.state:
                self.receive(msg,cid)
        elif cid is not None and (self.side is None or self.side == net.SIDE_SERVER):
            if self.peer.clients[cid].state == self.state:
                self.receive(msg,cid)
    def _send(self,msg,cid=None):
        if cid is None and (self.side is None or self.side == net.SIDE_CLIENT):
            if self.peer.remote_state == self.state:
                self.send(msg,cid)
        elif cid is not None and (self.side is None or self.side == net.SIDE_SERVER):
            if self.peer.clients[cid].state == self.state:
                self.send(msg,cid)

class PrintPacket(Packet):
    def receive(self,msg,cid=None):
        if cid is None:
            print("[CLIENT] Received message %s"%msg)
        else:
            print("[SERVER] Received message from %s: %s"%(cid,msg))
