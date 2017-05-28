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

import time
import sys

import peng3dnet

import common

def main(args):
    global run
    if len(args)==2:
        addr = args[1]
    else:
        addr = input("Server address:")
    
    client = peng3dnet.net.Client(addr=addr)
    
    client.register_packet("chat:message",common.MessagePacket(client.registry,client))
    
    
    def on_close(reason=None):
        global run
        print("Connection lost due to %s"%reason)
        print("Press enter to exit")
        run = False
    client.on_close = on_close
    
    client.runAsync()
    client.process_async()
    
    print("Type '/help' for command help")
    
    run = True
    while run:
        try:
            s = input()
        except KeyboardInterrupt:
            break
        if run == False:
            # if connection is closed
            return
        
        if s in ["/quit","/stop"]:
            run = False
            if s!="/stop":
                client.close_connection(reason="userrequest")
            elif s=="/stop":
                client.send_message("chat:message",{"message":"/stop"})
            client.join()
            continue
        
        client.send_message("chat:message",{"message":s,"timestamp":time.time()})

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
