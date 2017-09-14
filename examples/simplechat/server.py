#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  server.py
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

import sys
import time

import peng3dnet

import common

MAX_USERS = 128

class ClientOnChatServer(peng3dnet.net.ClientOnServer):
    def on_handshake_complete(self):
        super().on_handshake_complete()
        self.nickname="anonymous"
        print("Handshake with IP %s complete"%self.conn.getpeername()[0])
        #self.server.broadcast("User with IP Address %s joined the server"%(self.conn.getpeername()[0]),"server",internal=True,exclude_list=[self.cid])
    def on_close(self,reason=None):
        if self.conntype=="classic":
            self.server.broadcast("%s disconnected (%s)"%(getattr(self,"nickname","anonymous"),reason if reason is not None else "unknown"),"server",True)

class ChatServer(peng3dnet.ext.ping.PingableServerMixin,peng3dnet.net.Server):
    def broadcast(self,msg,origin,internal=False,private=False,timestamp=None,exclude_list=[]):
        if not self.is_server:
            raise RuntimeError("Cannot broadcast from client")
        print("Message: %s"%msg)
        data = {
            "message":msg,
            "origin":origin,
            "internal":internal,
            "private":private,
            "timestamp":timestamp if timestamp is not None else time.time(),
            }
        for client in self.clients:
            if client not in exclude_list:
                self.send_message("chat:message",data,client)
    
    def getPingData(self,msg,cid):
        users = [u for u in self.clients.values() if getattr(u,"nickname","anonymous")!="anonymous"]
        return {
            "usercount":len(users),
            "usersample":[u.nickname for u in users[:10]],
            "maxusers":MAX_USERS,
            "couldjoin":True, # dummy
            }

def main(args):
    if len(args)!=2:
        print("Not enough arguments!")
        sys.exit(1)
    
    server = ChatServer(addr=args[1],clientcls=ClientOnChatServer)
    
    server.cfg["net.ssl.server.certfile"]="testcerts/cert.pem"
    server.cfg["net.ssl.server.keyfile"]="testcerts/key.pem"
    server.cfg["net.ssl.cafile"]="testcerts/CAfile.pem"
    
    server.register_packet("chat:message",common.MessagePacket(server.registry,server))
    server.register_packet("chat:join",common.JoinPacket(server.registry,server))
    
    server.runAsync()
    server.process_forever()
    
    return 0
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
