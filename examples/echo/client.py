#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  client.py
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

import _thread

import peng3dnet

import common

def main(args):
    global run
    if len(args)!=2:
        print("Exactly one argument accepted")
    
    client = peng3dnet.net.Client(addr=args[1])
    
    client.register_packet("echo:echo",common.EchoPacket(client.registry,client))
    client.register_packet("echo:ping",common.PingPacket(client.registry,client))
    
    
    def on_close(reason=None):
        global run
        print("Connection closed due to %s"%reason)
        run = False
        _thread.interrupt_main()
    client.on_close = on_close
    
    client.runAsync()
    client.process_async()
    
    print("Type a message and press enter afterwards:")
    
    run = True
    while run:
        try:
            s = input()
        except KeyboardInterrupt:
            break
        if run == False:
            # if connection is closed
            return
        
        if s in ["quit","stop"]:
            run = False
            if s!="stop":
                client.close_connection(reason="userrequest")
            elif s=="stop":
                client.send_message("echo:echo","stop")
            client.join()
            continue
        elif s=="ping":
            client.send_message("echo:ping",{"client_timestamp":time.time()})
            continue
        client.send_message("echo:echo",s)
        print("Sent message to server, a response should appear within a second")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
