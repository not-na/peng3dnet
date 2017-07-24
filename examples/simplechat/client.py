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
    
    client.cfg["net.ssl.server.certfile"]="testcerts/cert.pem"
    client.cfg["net.ssl.server.keyfile"]="testcerts/key.pem"
    client.cfg["net.ssl.cafile"]="testcerts/CAfile.pem"
    
    client.register_packet("chat:message",common.MessagePacket(client.registry,client))
    client.register_packet("chat:join",common.JoinPacket(client.registry,client))
    
    def on_close(reason=None):
        global run
        print("Connection lost due to %s"%reason)
        print("Press enter to exit")
        run = False
    client.on_close = on_close
    
    client.runAsync()
    client.process_async()
    
    nickname = input("Nickname: ")
    if nickname == "":
        nickname = "anonymous"
    client.wait_for_connection(10)
    client.send_message("chat:join",{"nickname":nickname})
    
    print("Type '/help' for command help")
    
    run = True
    while run:
        try:
            s = input()
        except KeyboardInterrupt:
            break
        if run == False:
            # if connection is closed while waiting for input
            return
        
        if s in ["/quit","/stop"]:
            run = False
            if s=="/quit":
                client.close_connection(reason="userrequest")
            elif s=="/stop":
                client.send_message("chat:message",{"message":"/stop"})
            client.join()
            continue
        
        try:
            client.send_message("chat:message",{"message":s,"timestamp":time.time()})
        except Exception:
            print("Error while sending message:")
            import traceback;traceback.print_exc()
            print("Try reconnecting, that may solve this problem")
            run = False

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
