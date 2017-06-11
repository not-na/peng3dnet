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
import datetime

import peng3dnet
from peng3dnet.constants import *

def normalize_nickname(nick):
    nick = nick.strip() # remove all extraneous whitespace, makes impersonation by trailing spaces harder
    if nick=="":
        nick = "anonymous"
    elif len(nick)>32:
        nick = nick[:32] # trim it, probably the best way
    
    # Replaces unicode characters and special ascii chars with question marks, should (hopefully) prevent glitches and some exploits 
    out = ""
    for char in nick:
        if ord(char)>=0x7F or ord(char)<=0x1F:
            char = "?"
        out+=char
    
    return out

class MessagePacket(peng3dnet.packet.SmartPacket):
    mode = MODE_CHAT
    def receive(self,msg,cid=None):
        if self.peer.is_server:
            message = msg.get("message","")
            if message=="":
                return
            if message.startswith("/"):
                # Command
                command = message.split(" ")[0]
                args = message.split(" ")[1:]
                
                out = ""
                
                print("Received command %s with %s args"%(command,len(args)))
                
                if command=="/help":
                    out+="Command help:"
                    out+="\n/help             Lists basic help for all commands"
                    out+="\n/quit             Quits the client"
                    out+="\n/stop             Stops the server"
                    out+="\n/nick <name>      Changes the nickname"
                    out+="\n/whisper <name>   Sends a private message"
                elif command=="/quit":
                    # Should be handled by the client
                    pass
                elif command=="/stop":
                    self.peer.broadcast("Server will shutdown by request of user %s"%getattr(self.peer.clients[cid],"nickname","anonymous"),origin="server",internal=True,exclude_list=[cid])
                    try:
                        print("IP Address of User that shut down the server: %s"%self.peer.clients[cid].conn.getpeername()[0])
                    except Exception:
                        print("Could not determine IP Address of responsible user, connection may have been closed already.")
                    finally:
                        self.peer.shutdown(reason="command")
                elif command=="/nick":
                    if len(args)!=1:
                        out+="/nick expects exactly one argument"
                    else:
                        if args[0]=="anonymous":
                            out+="Forbidden nickname"
                        else:
                            nick = normalize_nickname(args[0])
                            out+="Changed nickname to '%s'"%nick
                            if getattr(self.peer.clients[cid],"nickname","anonymous")!="anonymous":
                                self.peer.broadcast("%s is now called %s"%(getattr(self.peer.clients[cid],"nickname","anonymous"),nick),origin="server",internal=True,exclude_list=[cid])
                            else:
                                self.peer.broadcast("%s has revealed themselves"%nick,"server",internal=True,exclude_list=[cid])
                            self.peer.clients[cid].nickname=nick
                elif command=="/whisper":
                    out+="Not yet implemented"
                elif command=="/anon":
                    if getattr(self.peer.clients[cid],"nickname","anonymous")!="anonymous":
                        self.peer.broadcast("%s has gone anonymous"%(getattr(self.peer.clients[cid],"nickname","anonymous")),origin="server",internal=True,exclude_list=[cid])
                        self.peer.clients[cid].nickname="anonymous"
                        out+="Gone anonymous"
                    else:
                        out+="Already anonymous"
                else:
                    out+="Unknown command '%s'"%command
                
                if out!="":
                    data = {
                        "message":out,
                        "origin":"server",
                        "timestamp":time.time(),
                        "internal":True,
                        "private":True,
                        }
                    self.peer.send_message("chat:message",data,cid)
                return
            # Redistribute to all clients except origin
            self.peer.broadcast(message,getattr(self.peer.clients[cid],"nickname","anonymous"),timestamp=msg.get("timestamp",None),exclude_list=[cid])
        elif self.peer.is_client:
            data = {"message":"","timestamp":time.time(),"origin":"anonymous","internal":False,"private":False}
            data.update(msg)
            internal,private = data["internal"],data["private"]
            ts = datetime.datetime.fromtimestamp(data["timestamp"])
            if not internal and not private:
                message = "[{0:%H:%M:%S}] {origin}: {message}".format(ts,**data)
            elif internal and not private:
                message = "[{0:%H:%M:%S}] {message}".format(ts,**data)
            elif internal and private:
                message = "[{0:%H:%M:%S}] {message}".format(ts,**data)
            elif not internal and private:
                message = "[{0:%H:%M:%S}] [PRIVATE] {origin}: {message}".format(ts,**data)
            print(message)

class JoinPacket(peng3dnet.packet.SmartPacket):
    side = SIDE_SERVER
    mode = MODE_NOTSET
    def send(self,msg,cid=None):
        self.peer.mode = MODE_CHAT
    def receive(self,msg,cid=None):
        nick = normalize_nickname(msg.get("nickname",self.peer.clients[cid].nickname))
        self.peer.clients[cid].mode = MODE_CHAT
        self.peer.clients[cid].nickname = nick
        self.peer.broadcast("User %s with IP Address %s joined the server"%(self.peer.clients[cid].nickname,self.peer.clients[cid].conn.getpeername()[0]),"server",internal=True,exclude_list=[cid])
