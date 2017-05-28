#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  conftest.py
#  
#  Copyright 2016 notna <notna@apparat.org>
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

import os
import threading

import pytest

import peng3dnet

EVENT_RECV = 1 << 0
EVENT_SEND = 1 << 1
EVENT_INTERNAL_PACKET = 1 << 2
EVENT_CONNECT = 1 << 3
EVENT_CLOSE = 1 << 4
EVENT_HANDSHAKE_FINISH = 1 << 5
EVENT_STATECHANGE = 1 << 6

DEFAULT_EVENTMASK = EVENT_RECV|EVENT_SEND|EVENT_CLOSE

class TestClientOnServer(peng3dnet.net.ClientOnServer):
    test_event_mask = DEFAULT_EVENTMASK
    
    def __init__(self,*args,**kwargs):
        self._state = peng3dnet.net.STATE_HANDSHAKE_WAIT1
        super().__init__(*args,**kwargs)
        
        self.test_event_log = []
        self.test_event_lock = threading.Lock()
        self.test_close_condition = threading.Condition()
    
    def log_test_event(self,data,evtype):
        if self.test_event_mask&evtype:
            with self.test_event_lock:
                self.test_event_log.append([evtype,data])
                if evtype==EVENT_CLOSE:
                    with self.test_close_condition:
                        self.test_close_condition.notify_all()
    def clear_events(self):
        with self.test_event_lock:
            self.test_event_log = []
    def wait_for_close(self,timeout=10.0):
        def f():
            for data,ev in self.test_event_log:
                if ev==EVENT_CLOSE:
                    return True
            return False
        with self.test_close_condition:
            self.test_close_condition.wait_for(f,timeout)
    
    @property
    def state(self):
        return self._state
    @state.setter
    def state(self,value):
        self._state = value
        self.log_test_event(value,EVENT_STATECHANGE)
    
    def on_handshake_complete(self):
        super().on_handshake_complete()
        self.log_test_event(None,EVENT_HANDSHAKE_FINISH)
    def on_close(self,reason=None):
        super().on_close(reason)
        self.log_test_event(reason,EVENT_CLOSE)
    def on_connect(self):
        super().on_connect()
        self.log_test_event(None,EVENT_CONNECT)
    def on_receive(self,*args):
        super().on_recv(*args)
        args[0]=self.server.registry.getName(args[0])
        if (not args[0].startswith("peng3dnet:internal.")) or self.test_event_mask&EVENT_INTERNAL_PACKET:
            self.log_test_event(args,EVENT_RECV)
    def on_send(self,*args):
        super().on_send(*args)
        args[0]=self.server.registry.getName(args[0])
        if (not args[0].startswith("peng3dnet:internal.")) or self.test_event_mask&EVENT_INTERNAL_PACKET:
            self.log_test_event(args,EVENT_SEND)

def create_test_server(addr="localhost",port=11234,event_mask=DEFAULT_EVENTMASK):
    class _cls(TestClientOnServer):
        test_event_mask = event_mask
    server = peng3dnet.net.Server((addr,port),_cls)
    return server
