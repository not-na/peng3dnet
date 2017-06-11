#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ping.py
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
import threading

from ..constants import *
from .. import packet
from .. import version
from .. import util
from .. import net
from .. import errors
from .. import conntypes

class PingConnectionType(conntypes.ConnectionType):
    def init(self,cid):
        if cid is None:
            # on client
            self.peer._ping()
            self.peer.remote_state = STATE_ACTIVE
        else:
            # on server
            self.peer.clients[cid].state = STATE_ACTIVE
    def receive(self,msg,pid,flags,cid):
        if pid==64:
            if cid is None:
                self.peer.close_connection(cid,"pinginvalidside")
            
            # Ping, recv on server
            self.peer.clients[cid].mode = MODE_PING
            # Luckily, we're in Python and arent vulnerable to stuff like Heartbleed
            # If this were in C++, this would mean some trouble
            data = {"oldmsg":msg}
            
            if hasattr(self.peer,"getPingData") and callable(self.peer.getPingData):
                data.update(self.peer.getPingData(msg,cid))
            if hasattr(self.peer,"pingdata"):
                data.update(self.peer.pingdata)
            data.update(self.getPingData(msg,cid))
            
            self.peer.send_message(65,data,cid)
            
            #self.peer.close_connection(cid,"pingcomplete")
        elif pid==65:
            if cid is not None:
                self.peer.close_connection(cid,"pinginvalidside")
            
            # Pong, recv on client
            try:
                if hasattr(self.peer,"on_pong") and callable(self.peer.on_pong):
                    self.peer.on_pong(msg)
                self.peer._pong(msg)
            finally:
                self.peer.close_connection(reason="pingcomplete")
        else:
            self.peer.close_connection(cid,"invalidpingpacket")
        
        return True
    
    def send(self,msg,pid,cid):
        if pid==64:
            self.peer.mode = MODE_PING
            # Ping, send from client
        elif pid==65:
            # Pong, send from server
            pass
        else:
            raise ValueError("Invalid packet id %s detected"%pid)
        
        return True
    
    def getPingData(self,msg,cid=None):
        return {"peng3dnet":{"version":version.VERSION,"release":version.RELEASE,"protoversion":version.PROTOVERSION}}

class PingableServerMixin(object):
    # Add static data like MOTD etc. here
    pingdata = {}
    def getPingData(self,msg,cid):
        # Add dynamic data like User count etc. here
        return {}
    
    #def _reg_packets_ping(self):
    #    self.register_packet("peng3dnet:ping",PingPacket(self.registry,self))
    #    self.register_packet("peng3dnet:pong",PongPacket(self.registry,self))
    
    def _reg_conntypes_ping(self):
        self.addConnType("ping",PingConnectionType(self))

class PingableClientMixin(object):
    #def _reg_packets_ping(self):
    #    self.register_packet("peng3dnet:ping",PingPacket(self.registry,self))
    #    self.register_packet("peng3dnet:pong",PongPacket(self.registry,self))
    
    _pingdata = None
    _pongdata = None
    
    _pong_condition = threading.Condition()
    
    def _reg_conntypes_ping(self):
        self.addConnType("ping",PingConnectionType(self))
    
    def setPingData(self,d):
        self._pingdata = d
    
    def _ping(self):
        self.send_message(64,self._pingdata)
    
    def _pong(self,data):
        with self._pong_condition:
            self._pongdata = data
            self._pong_condition.notify_all()
    
    def wait_for_pong(self,timeout=None):
        with self._pong_condition:
            if self._pongdata is not None:
                return self._pongdata
            if not self._pong_condition.wait_for(lambda: self._pongdata is not None,timeout):
                raise errors.FailedPingError("Timed out")
            return self._pongdata

class _PingClient(PingableClientMixin,net.Client):
    pass

def pingServer(peng=None,addr=None,cfg={},data={},clientcls=_PingClient,timeout=10.0):
    client = clientcls(peng,addr,cfg,CONNTYPE_PING)
    
    client.setPingData({"time":time.time()})
    
    # Needs this weird hack with a dictionary because of namespaces
    d = {"data":None}
    
    def on_pong(msg):
        data = msg
        data["recvtime"]=time.time()
        d["data"]=data
        client.close_connection("pingcomplete")
    client.on_pong = on_pong
    
    client.runAsync()
    client.process_async()
    
    client.wait_for_pong(timeout)
    
    data = d["data"]
    
    if data is None:
        raise errors.FailedPingError("No answer received")
    
    data["delay"]=data["recvtime"]-data["oldmsg"]["time"]
    return data
    
