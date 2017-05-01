#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  common.py
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

import time

import peng3dnet

class EchoPacket(peng3dnet.packet.SmartPacket):
    def receive(self,msg,cid=None):
        if self.peer.is_server:
            print("Received message from client %s: %s"%(cid,msg))
            # Server replies with same packet
            if msg=="stop":
                self.peer.close_connection(cid,"command")
                self.peer.shutdown()
                return
            self.peer.send_message("echo:echo",msg,cid)
        elif self.peer.is_client:
            print("Received from server: %s"%msg)

class PingPacket(peng3dnet.packet.SmartPacket):
    def receive(self,msg,cid=None):
        if self.peer.is_server:
            # Server immediately returns packet, with timestamp added
            msg["server_timestamp"]=time.time()
            self.peer.send_message("echo:ping",msg,cid)
        elif self.peer.is_client:
            t_c = msg["client_timestamp"]
            t_s = msg["server_timestamp"]
            t_a = time.time()
            print("Received ping answer: %.2fms total, %.2fms client-server and %.2fms server-client"%((t_a-t_c)*1000,(t_s-t_c)*1000,(t_a-t_s)*1000))
