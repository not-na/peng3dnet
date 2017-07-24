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
"""
The ping extension was designed to allow a client to check on various values the server provides without much effort.
It allows the client to check on metrics such as latency and additional values able to be customized by the server.

This extension is named after the UNIX :command:`ping` utility, though it can do much more than just check on availability and latency.
"""

import time
import threading

from ..constants import *
from .. import packet
from .. import version
from .. import util
from .. import net
from .. import errors
from .. import conntypes

WRITEBACK = True
"""
Constant allowing to configure if the received ping message should be transmitted back to the client.

If there should ever be any security concerns regarding that feature, this flag can simply be flipped.
"""

class PingConnectionType(conntypes.ConnectionType):
    """
    Connection type to be used by ping connections.
    
    This connection type prevents any synchronization of the registry to allow
    clients only supporting a subset of the peng3dnet protocol to still ping a server.
    
    Additonally, conventional processing of packets will be disabled by this connection type,
    making it uneccessary to register packets with the client or server.
    """
    def init(self,cid):
        """
        Called whenever a new ping connection is established.
        
        On the client, this calls :py:meth:`PingableClientMixin._ping()` and updates
        the connection state, while on the server only the connection state is updated.
        """
        if cid is None:
            # on client
            self.peer._ping()
            self.peer.remote_state = STATE_ACTIVE
        else:
            # on server
            self.peer.clients[cid].state = STATE_ACTIVE
    def receive(self,msg,pid,flags,cid):
        """
        Called whenever a packet is received via this connection type.
        
        Handles any ping requests and pong answers and always returns ``True`` to skip any further processing.
        """
        if pid==64:
            if cid is None:
                self.peer.close_connection(cid,"pinginvalidside")
            
            # Ping, recv on server
            self.peer.clients[cid].mode = MODE_PING
            
            if WRITEBACK:
                # Luckily, we're in Python and arent vulnerable to stuff like Heartbleed
                # If this were in C++, this would mean some trouble
                data = {"oldmsg":msg}
            else:
                data = {}
            
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
        """
        Called whenever a packet is sent via this connection type.
        """
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
        """
        Overridable method to create a ping response.
        
        ``msg`` is the ping query, as received from the client.
        
        ``cid`` is the ID of the client.
        
        Called only on the server side.
        """
        return {"peng3dnet":{"version":version.VERSION,"release":version.RELEASE,"protoversion":version.PROTOVERSION}}

class PingableServerMixin(object):
    """
    Mixin for :py:class:`~peng3dnet.net.Server` classes enabling support for pinging the server.
    
    Currently automatically adds the ``ping`` connection type.
    """
    # Add static data like MOTD etc. here
    pingdata = {}
    """
    Overrideable dictionary used to extend the default dictionary returned upon a ping request.
    
    May be overriden to add static data like server name or similiar information.
    """
    def getPingData(self,msg,cid):
        """
        Overrideable method called to extend the default dictionary returned upon a ping request.
        
        May be overriden to add dynamic data like user count or similiar information.
        
        ``msg`` is the original message as received from the client.
        
        ``cid`` is the client ID that made this request.
        """
        # Add dynamic data like User count etc. here
        return {}
    
    #def _reg_packets_ping(self):
    #    self.register_packet("peng3dnet:ping",PingPacket(self.registry,self))
    #    self.register_packet("peng3dnet:pong",PongPacket(self.registry,self))
    
    def _reg_conntypes_ping(self):
        self.addConnType("ping",PingConnectionType(self))

class PingableClientMixin(object):
    """
    Mixin for :py:class:`~peng3dnet.net.Client` classes enabling support for pinging the server.
    
    Currently automatically adds the ``ping`` connection type.
    """
    #def _reg_packets_ping(self):
    #    self.register_packet("peng3dnet:ping",PingPacket(self.registry,self))
    #    self.register_packet("peng3dnet:pong",PongPacket(self.registry,self))
    
    _pingdata = None
    _pongdata = None
    
    _pong_condition = threading.Condition()
    
    def _reg_conntypes_ping(self):
        self.addConnType("ping",PingConnectionType(self))
    
    def setPingData(self,d):
        """
        Sets the data to add to any ping responses.
        
        Repeated calls of this method will overwrite previous data.
        """
        self._pingdata = d
    
    def _ping(self):
        """
        Handler called by :py:meth:`PingConnectionType.init()` when a ping connection is established.
        
        By default, this sends a ping packet to the server.
        """
        self.send_message(64,self._pingdata)
    
    def _pong(self,data):
        with self._pong_condition:
            self._pongdata = data
            self._pong_condition.notify_all()
    
    def wait_for_pong(self,timeout=None):
        """
        Waits up to ``timeout`` seconds for a ping response to arrive.
        
        If a response has already been received, this method returns immediately.
        
        If the ping was successful, the received message is returned.
        """
        with self._pong_condition:
            if self._pongdata is not None:
                return self._pongdata
            if not self._pong_condition.wait_for(lambda: self._pongdata is not None,timeout):
                raise errors.FailedPingError("Timed out")
            return self._pongdata

class _PingClient(PingableClientMixin,net.Client):
    pass

def pingServer(peng=None,addr=None,cfg={},data={},clientcls=_PingClient,timeout=10.0):
    """
    Pings the specified server.
    
    Internally, this creates a client that supports pinging and listens for any data received back.
    
    ``peng`` may be optionally used to replace the argument of the same name to :py:class:`~peng3dnet.net.Client()`\ .
    
    ``addr`` specifies the address of the server to ping.
    
    ``cfg`` may be used to override the configuration for the client, e.g. SSL settings.
    
    ``data`` is the data sent to the server. Note that the ``time`` key will be overridden for measuring the latency.
    
    ``clientcls`` may be used to override the client class used.
    
    ``timeout`` is maximum amount of time to wait for a response.
    
    The data returned will be the data received from the server, except for
    additional information that has been added. Currently, the ``recvtime`` key
    contains the timestamp that the response was received and the ``delay`` key
    contains the total roundtrip time in seconds.
    """
    client = clientcls(peng,addr,cfg,CONNTYPE_PING)
    
    data["time"]=time.time()
    client.setPingData(data)
    
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
    
