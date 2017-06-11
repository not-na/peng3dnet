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
    def __init__(self,peer):
        self.peer = peer
    def init(self,cid):
        # Return value of true would cause halting of processing
        pass
    def receive(self,msg,pid,flags,cid):
        return False
    def send(self,data,pid,cid):
        return False

class ClassicConnectionType(ConnectionType):
    def init(self,cid):
        if cid is not None:
            self.peer.clients[cid].state = STATE_HANDSHAKE_WAIT1
            self.peer.send_message("peng3dnet:internal.handshake",{"version":version.VERSION,"protoversion":version.PROTOVERSION,"registry":dict(self.peer.registry.reg_int_str._inv)},cid)
        elif cid is None:
            self.peer.remote_state = STATE_HANDSHAKE_WAIT1
