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

import peng3dnet

import common

class ClientOnEchoServer(peng3dnet.net.ClientOnServer):
    def on_handshake_complete(self):
        super().on_handshake_complete()
        print("Client %s connected"%self.cid)
    def on_close(self,reason=None):
        print("Client %s disconnected due to %s"%(self.cid,reason))

def main(args):
    if len(args)!=2:
        print("Not enough arguments!")
        sys.exit(1)
    
    server = peng3dnet.net.Server(addr=args[1],clientcls=ClientOnEchoServer)
    
    server.register_packet("echo:echo",common.EchoPacket(server.registry,server))
    server.register_packet("echo:ping",common.PingPacket(server.registry,server))
    
    server.runAsync()
    server.process_forever()
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
