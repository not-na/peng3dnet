#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  net.py
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

__all__ = [
    "Server","ClientOnServer",
    "Client",
    ]

import sys
import time
import struct
import threading
import socket
import selectors

if sys.version_info.major==2:
    import Queue
elif sys.version_info.major==3:
    import queue as Queue
else:
    raise ValueError("Python version %s is not supported"%sys.version) # for old python 1.x or python 4.x if that happens to ever exist

try:
    import msgpack as msgpack
except ImportError:
    import umsgpack as msgpack

import peng3d

from . import version
from . import packet
from . import util
from . import registry
from .constants import *

STRUCT_HEADER = struct.Struct(STRUCT_FORMAT_HEADER)
STRUCT_LENGTH32 = struct.Struct(STRUCT_FORMAT_LENGTH32)

class Server(object):
    def __init__(self,peng=None,addr=None,clientcls=None,cfg={}):
        if peng is None:
            self.cfg = peng3d.config.Config(cfg,DEFAULT_CONFIG)
        else:
            ncfg = {}
            ncfg.update(DEFAULT_CONFIG)
            ncfg.update(cfg)
            self.cfg = peng3d.config.Config(ncfg,peng.cfg)
        if addr is not None:
            addr = util.normalize_addr_socketstyle(addr,self.cfg["net.server.addr.port"])
            self.cfg["net.server.addr.host"]=addr[0]
            self.cfg["net.server.addr.port"]=addr[1]
        elif self.cfg["net.server.addr"] is None:
            addr = util.normalize_addr_socketstyle(self.cfg["net.server.addr.host"],self.cfg["net.server.addr.port"])
        else:
            addr = util.normalize_addr_socketstyle(self.cfg["net.server.addr"],self.cfg["net.server.addr.port"])
        if self.cfg["net.events.enable"]=="auto":
            self.cfg["net.events.enable"]=peng is not None
        
        self.peng = peng
        
        self.addr = addr
        
        self.is_client = False
        self.is_server = True
        self.side = SIDE_SERVER
        
        self.sock = None
        self._sock_lock = threading.Lock()
        
        self.selector = None
        self._selector_lock = threading.Lock()
        
        self._next_cid = 1
        self._cid_lock = threading.Lock()
        
        self._init_lock = threading.Lock()
        
        self._is_bound = False
        self._is_started = False
        self._is_initialized = False
        
        self._irqrecv = None
        self._irqsend = None
        
        self.clientcls = clientcls if clientcls is not None else ClientOnServer
        
        self._run_thread = None
        self._process_thread = None
        
        self._process_queue = Queue.Queue()
        self._process_condition = threading.Condition()
        
        self.run = True
        self.clients = {}
        
        self.registry = registry.PacketRegistry()
    
    def initialize(self):
        if self._is_initialized:
            return
        with self._init_lock:
            if self._is_initialized:
                return
            
            from .packet import internal
            
            self.register_packet("peng3dnet:internal.handshake",internal.HandshakePacket(self.registry,self),1)
            self.register_packet("peng3dnet:internal.handshake.accept",internal.HandshakeAcceptPacket(self.registry,self),2)
            
            self.register_packet("peng3dnet:internal.closeconn",internal.CloseConnectionPacket(self.registry,self),16)
            
            self.sendEvent("peng3dnet:server.initialize",{})
    
    def bind(self):
        if self._is_bound:
            return
        with self._sock_lock:
            if self._is_bound:
                return
            
            self._irqrecv,self._irqsend = socket.socketpair()
            
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            # Use only if debugging, prevents address in use errors (ERRNO 98)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(tuple(self.addr))
            self.sock.listen(100)
            self.sock.setblocking(False)
            
            self._is_bound = True
            
            self.sendEvent("peng3dnet:server.bind",{"addr":tuple(self.addr)})
    
    def runBlocking(self,selector=selectors.DefaultSelector):
        if self._is_started:
            return
        self.initialize()
        self.bind()
        with self._selector_lock:
            if self._is_started:
                return
            
            self.selector = selector()
            self.selector.register(self.sock,selectors.EVENT_READ,[self._accept,self])
            
            self.selector.register(self._irqrecv,selectors.EVENT_READ,[self._client_ready,None])
            self.selector.register(self._irqsend,selectors.EVENT_READ,[self._client_ready,None])
            
            self._is_started = True
            self.sendEvent("peng3dnet:server.start",{})
        
        while self.run:
            events = self.selector.select()
            for key,mask in events:
                callback,data = key.data
                try:
                    callback(key.fileobj, mask, data)
                except Exception:
                    import traceback;traceback.print_exc()# Ignore exceptions for now...
    
    def runAsync(self,selector=selectors.DefaultSelector):
        self._run_thread = threading.Thread(name="peng3dnet Server Thread",target=self.runBlocking,args=[selector])
        self._run_thread.daemon = True
        self._run_thread.start()
    def stop(self):
        self.run = False
        self.sendEvent("peng3dnet:server.stop",{"reason":"method"})
        self.interrupt()
    def interrupt(self):
        # simply wakes the main loop up
        # used to force a check if the system is still running
        self._irqsend.sendall(b"wake up!")
        self.sendEvent("peng3dnet:server.interrupt",{})
    
    def shutdown(self,join=True,timeout=0,reason="servershutdown"):
        for cid in self.clients:
            try:
                self.close_connection(cid,reason)
                #self.send_message("peng3d:internal.closeconn",{"reason":"servershutdown"})
            except Exception:
                pass
        if join:
            # TODO
            t = time.time()
            while len(self.clients)>0 and time.time()-t<timeout:
                time.sleep(0.01)
        self.stop()
        self.sendEvent("peng3dnet:server.shutdown",{"reason":reason,"join":join,"timeout":timeout})
        if join:
            self.join(timeout-(time.time()-t))
    def join(self,timeout=None):
        self.stop()
        ft = time.time()+timeout if timeout is not None else 1
        if self._run_thread is not None:
            if timeout is None:
                self._run_thread.join()
            else:
                self._run_thread.join(max(ft-time.time(),0))
        if self._process_thread is not None:
            if timeout is None:
                self._process_thread.join()
            else:
                self._process_thread.join(max(ft-time.time(),0))
    
    def _accept(self,sock,mask,data):
        conn,addr = sock.accept()
        conn.setblocking(False)
        
        client = self.clientcls(self,conn,addr,self.genCID())
        self.clients[client.cid]=client
        
        with self._selector_lock:
            self.selector.register(conn,selectors.EVENT_READ,[self._client_ready,client])
        
        client.on_connect()
        self.send_message("peng3dnet:internal.handshake",{"version":version.VERSION,"protoversion":version.PROTOVERSION,"registry":dict(self.registry.reg_int_str._inv)},client.cid)
        self.sendEvent("peng3dnet:server.connection.accept",{"sock":conn,"addr":addr,"client":client,"cid":client.cid})
    
    def _client_ready(self,conn,mask,data):
        if (mask & selectors.EVENT_READ):
            # Socket Readable
            if conn==self._irqrecv:
                dat = conn.recv(8)
                if dat!=b"wake up!":
                    conn.sendall(b"wrong socket")
                return
            elif conn==self._irqsend:
                # should not happen
                dat = conn.recv(1024)
                return
            
            dat = conn.recv(1024)
            if dat:
                # Non-empty
                try:
                    self.receive_data(dat,data.cid)
                except Exception:
                    import traceback;traceback.print_exc()
            else:
                # Closed connection
                with self._selector_lock:
                    self.selector.unregister(conn)
                data.close()
                del self.clients[data.cid]
        
        if (mask & selectors.EVENT_WRITE):
            # Socket Writeable
            if data is None:
                return # IRQ Socket
            
            try:
                msg = data.write_queue.get_nowait()
            except Queue.Empty:
                self.selector.modify(conn,selectors.EVENT_READ,[self._client_ready,data])
            else:
                conn.sendall(msg)
                if data.write_queue.empty():
                    self.selector.modify(conn,selectors.EVENT_READ,[self._client_ready,data])
            
            if data._mark_close and data.write_queue.empty():
                with self._selector_lock:
                    self.selector.unregister(conn)
                data.close()
                del self.clients[data.cid]
    
    def genCID(self):
        with self._cid_lock:
            cid = self._next_cid
            self._next_cid+=1
            return cid
    
    def receive_data(self,data,cid):
        client = self.clients[cid]
        
        # Length prefix code
        client._buf+=data
        while (client._buflen is None and len(client._buf)>0) or (client._buflen is not None and len(client._buf)>=client._buflen):
            self.process_single_packet(client)
    def receive_packet(self,data,cid):
        self._process_queue.put([cid,data])
        with self._process_condition:
            self._process_condition.notify()
    
    def send_message(self,ptype,data,cid):
        self.clients[cid].on_send(ptype,data)
        self.sendEvent("peng3dnet:server.connection.send",{"client":self.clients[cid],"pid":ptype,"data":data})
        self.registry.getObj(ptype)._send(data,cid)
        
        data = msgpack.dumps(data)
        
        flags = 0
        
        if len(data)>COMPRESS_THRESHOLD:
            data = zlib.compress(data,COMPRESS_LEVEL)
            flags = flags|FLAG_COMPRESSED
        
        header = STRUCT_HEADER.pack(self.registry.getInt(ptype),flags)
        data = header+data
        
        prefix = STRUCT_LENGTH32.pack(len(data))
        data = prefix+data
        
        self.clients[cid].write_queue.put(data)
        if not (self.selector.get_key(self.clients[cid].conn).events&selectors.EVENT_WRITE):
            # Prevents unneccessary modification if nothing changes
            self.selector.modify(self.clients[cid].conn,selectors.EVENT_READ|selectors.EVENT_WRITE,[self._client_ready,self.clients[cid]])
            self.interrupt() # forces the changes to apply
    
    def process_single_packet(self,client):
        if client._buflen is None:
            # Previous packet has been processed, begin new packet
            if len(client._buf)<STRUCT_LENGTH32.size:
                # Prevents errors
                return
            client._buflen = STRUCT_LENGTH32.unpack(client._buf[:STRUCT_LENGTH32.size])[0]
            client._buf = client._buf[STRUCT_LENGTH32.size:]
            if client._buflen>MAX_PACKETLENGTH:
                # Should be pretty rare, but still
                raise ValueError("Packet too long")
        
        if len(client._buf)>=client._buflen:
            # Enough data has been gathered, process it
            data = client._buf[:client._buflen]
            client._buf = client._buf[client._buflen:]
            client._buflen = None
            self.receive_packet(data,client.cid)
    
    def register_packet(self,name,obj,n=None):
        self.registry.register(obj,name,n)
    
    def close_connection(self,cid,reason=None):
        # not removed immediately to ensure that the reason is transmitted
        self.send_message("peng3dnet:internal.closeconn",{"reason":reason},cid)
        self.clients[cid]._mark_close = True
    
    def process(self,wait=False,timeout=None):
        if wait:
            with self._process_condition:
                self._process_condition.wait(timeout)
        n = 0
        while not (self._process_queue.empty()):
            try:
                cid,data = self._process_queue.get_nowait()
            except Queue.Empty:
                break # may happen rarely
            else:
                header,body = data[:STRUCT_HEADER.size],data[STRUCT_HEADER.size:]
                pid,flags = STRUCT_HEADER.unpack(header)
                
                if flags&FLAG_COMPRESSED:
                    body = zlib.decompress(body)
                if flags&FLAG_ENCRYPTED_AES:
                    raise NotImplementedError("Encryption not yet implemented")
                
                # Due to https://github.com/msgpack/msgpack-python/issues/99
                msg = msgpack.unpackb(body,encoding="utf-8")
                
                try:
                    client = self.clients[cid]
                    self.registry.getObj(pid)._receive(msg,cid)
                    client.on_receive(pid,msg)
                    self.sendEvent("peng3dnet:server.connection.recv",{"client":client,"pid":pid,"msg":msg})
                except Exception:
                    import traceback;traceback.print_exc()
                n+=1
        return n
    
    def process_forever(self):
        while self.run:
            # TODO: make interruptable
            self.process(wait=True,timeout=0.01)
    def process_async(self):
        self._process_thread = threading.Thread(name="peng3dnet process Thread",target=self.process_forever)
        self._process_thread.daemon = True
        self._process_thread.start()
    
    def sendEvent(self,event,data={}):
        if self.cfg["net.events.enable"]:
            if isinstance(data,dict):
                data["peng"]=self.peng
                data["server"]=self.server
            self.peng.sendEvent(event,data)

class ClientOnServer(object):
    def __init__(self,server,conn,addr,cid):
        self.server = server
        self.conn = conn
        self.addr = addr
        self.cid = cid
        
        self.write_queue = Queue.Queue()
        
        self.name = None
        
        self._buf = bytes()
        self._buflen = None
        
        self._mark_close = False
        
        self.state = STATE_HANDSHAKE_WAIT1
    
    def close(self,reason=None):
        self.server.sendEvent("peng3dnet:server.connection.close",{"client":self,"reason":reason})
        self.state = STATE_CLOSED
        try:
            self.server.selector.unregister(self.conn)
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass
        if self.state!=STATE_CLOSED:
            self.on_close(reason)
    
    def on_handshake_complete(self):
        self.server.sendEvent("peng3dnet:server.connection.handshakecomplete",{"client":self})
        self.state = STATE_ACTIVE
    def on_close(self,reason=None):
        pass
    def on_connect(self):
        pass
    def on_receive(self,ptype,msg):
        pass
    def on_send(self,ptype,msg):
        pass
        
class Client(object):
    def __init__(self,peng=None,addr=None,cfg={}):
        if peng is None:
            self.cfg = peng3d.config.Config(cfg,DEFAULT_CONFIG)
        else:
            ncfg = {}
            ncfg.update(DEFAULT_CONFIG)
            ncfg.update(cfg)
            self.cfg = peng3d.config.Config(ncfg,peng.cfg)
        if addr is not None:
            addr = util.normalize_addr_socketstyle(addr,self.cfg["net.client.addr.port"])
            self.cfg["net.client.addr.host"]=addr[0]
            self.cfg["net.client.addr.port"]=addr[1]
        elif self.cfg["net.client.addr"] is None:
            addr = util.normalize_addr_socketstyle(self.cfg["net.client.addr.host"],self.cfg["net.client.addr.port"])
        else:
            addr = util.normalize_addr_socketstyle(self.cfg["net.client.addr"],self.cfg["net.client.addr.port"])
        if self.cfg["net.events.enable"]=="auto":
            self.cfg["net.events.enable"]=peng is not None
        
        self.peng = peng
        
        self.addr = addr
        
        self.is_client = True
        self.is_server = False
        self.side = SIDE_CLIENT
        
        self.sock = None
        self._sock_lock = threading.Lock()
        
        self.selector = None
        self._selector_lock = threading.Lock()
        
        self._init_lock = threading.Lock()
        
        self._process_queue = Queue.Queue()
        self._process_condition = threading.Condition()
        
        self._is_connected = False
        self._is_started = False
        self._is_initialized = False
        
        self._irqrecv = None
        self._irqsend = None
        
        self._mark_close = False
        self._close_reason = None
        
        self._run_thread = None
        self._process_thread = None
        
        self.run = True
        
        self._buf = bytes()
        self._buflen = None
        
        self._write_buf = b""
        
        self.remote_state = STATE_INIT
        
        self.registry = registry.PacketRegistry()
    
    def initialize(self):
        if self._is_initialized:
            return
        with self._init_lock:
            if self._is_initialized:
                return
            
            from .packet import internal
            
            self.register_packet("peng3dnet:internal.handshake",internal.HandshakePacket(self.registry,self),1)
            self.register_packet("peng3dnet:internal.handshake.accept",internal.HandshakeAcceptPacket(self.registry,self),2)
            
            self.register_packet("peng3dnet:internal.closeconn",internal.CloseConnectionPacket(self.registry,self),16)
            
            self.sendEvent("peng3dnet:client.initialize",{})
    
    def connect(self):
        if self._is_connected:
            return
        with self._sock_lock:
            if self._is_connected:
                return
            
            self._irqrecv,self._irqsend = socket.socketpair()
            
            self.sock = socket.create_connection(tuple(self.addr))
            self.sock.setblocking(True)
            
            self._is_connected = True
            
            self.sendEvent("peng3dnet:client.connect",{"addr":tuple(self.addr),"sock":self.sock})
    
    def runBlocking(self,selector=selectors.DefaultSelector):
        if self._is_started:
            return
        self.initialize()
        self.connect()
        with self._selector_lock:
            if self._is_started:
                return
            
            self.selector = selector()
            self.selector.register(self.sock,selectors.EVENT_READ,[self._sock_ready,self])
            
            self.selector.register(self._irqrecv,selectors.EVENT_READ,[self._sock_ready,None])
            self.selector.register(self._irqsend,selectors.EVENT_READ,[self._sock_ready,None])
            
            self._is_started = True
            
            self.sendEvent("peng3dnet:client.start",{})
        
        while self.run:
            events = self.selector.select()
            for key,mask in events:
                callback,data = key.data
                try:
                    callback(key.fileobj, mask, data)
                except Exception:
                    import traceback;traceback.print_exc() # Ignore exceptions for now...
    def runAsync(self,selector=selectors.DefaultSelector):
        self._run_thread = threading.Thread(name="peng3dnet Client Thread",target=self.runBlocking,args=[selector])
        self._run_thread.daemon = True
        self._run_thread.start()
    def stop(self):
        self.run = False
        self.sendEvent("peng3dnet:client.stop",{"reason":"method"})
        self.interrupt()
    def interrupt(self):
        # simply wakes the main loop up
        # used to force a check if the system is still running
        self._irqsend.sendall(b"wake up!")
        self.sendEvent("peng3dnet:client.interrupt",{})
    
    def _sock_ready(self,sock,mask,data):
        if sock==self._irqrecv:
            dat = sock.recv(8)
            if dat!=b"wake up!":
                sock.sendall(b"wrong socket")
            return
        elif sock==self._irqsend:
            # should not happen
            sock.recv(1024)
            return
        if (mask & selectors.EVENT_READ):
            # Readable
            
            dat = sock.recv(1024)
            if dat:
                # Non-empty
                try:
                    self.receive_data(dat)
                except Exception:
                    import traceback;traceback.print_exc()
            else:
                self.close("socketclose")
        
        if (mask & selectors.EVENT_WRITE):
            # Writeable
            
            self.pump_write_buffer()
    
    def send_message(self,ptype,data,cid=None):
        self.on_send(ptype,data)
        self.sendEvent("peng3dnet:client.send",{"pid":ptype,"data":data})
        self.registry.getObj(ptype)._send(data)
        
        data = msgpack.dumps(data)
        
        flags = 0
        
        if len(data)>COMPRESS_THRESHOLD:
            data = zlib.compress(data,COMPRESS_LEVEL)
            flags = flags|FLAG_COMPRESSED
        
        header = STRUCT_HEADER.pack(self.registry.getInt(ptype),flags)
        data = header+data
        
        prefix = STRUCT_LENGTH32.pack(len(data))
        data = prefix+data
        
        self._write_buf+=bytes(data)
        
        self.pump_write_buffer()
    
    def pump_write_buffer(self):
        if len(self._write_buf)==0:
            return
        
        try:
            bytes_sent = self.sock.send(self._write_buf,socket.MSG_DONTWAIT)
            self._write_buf = self._write_buf[bytes_sent:]
            if len(self._write_buf)==0:
                if self._mark_close:
                    with self._selector_lock:
                        self.selector.unregister(sock)
                    self.on_close(self._close_reason)
                return # sent everything in one go
            if not (self.selector.get_key(self.sock).events&selectors.EVENT_WRITE):
                self.selector.modify(self.sock,selectors.EVENT_READ|selectors.EVENT_WRITE,[self._sock_ready,None])
                self.interrupt()
        except Exception:
            import traceback;traceback.print_exc()
    
    def receive_data(self,data,cid=None):
        # Length prefix code
        self._buf+=data
        while (self._buflen is None and len(self._buf)>0) or (self._buflen is not None and len(self._buf)>=self._buflen):
            self.process_single_packet()
    def receive_packet(self,data,cid=None):
        self._process_queue.put([None,data])
        with self._process_condition:
            self._process_condition.notify()
    
    def process_single_packet(self,client=None):
        if self._buflen is None:
            # Previous packet has been processed, begin new packet
            if len(self._buf)<STRUCT_LENGTH32.size:
                # Prevents errors
                return
            self._buflen = STRUCT_LENGTH32.unpack(self._buf[:STRUCT_LENGTH32.size])[0]
            self._buf = self._buf[STRUCT_LENGTH32.size:]
            if self._buflen>MAX_PACKETLENGTH:
                # Should be pretty rare, but still
                raise ValueError("Packet too long")
        
        if len(self._buf)>=self._buflen:
            # Enough data has been gathered, process it
            data = self._buf[:self._buflen]
            self._buf = self._buf[self._buflen:]
            self._buflen = None
            self.receive_packet(data)
    
    def register_packet(self,name,obj,n=None):
        self.registry.register(obj,name,n)
    
    def process(self,wait=False,timeout=None):
        if wait:
            with self._process_condition:
                self._process_condition.wait(timeout)
        n = 0
        while not (self._process_queue.empty()):
            try:
                _,data = self._process_queue.get_nowait()
            except Queue.Empty:
                break # may happen rarely
            else:
                header,body = data[:STRUCT_HEADER.size],data[STRUCT_HEADER.size:]
                pid,flags = STRUCT_HEADER.unpack(header)
                
                if flags&FLAG_COMPRESSED:
                    body = zlib.decompress(body)
                if flags&FLAG_ENCRYPTED_AES:
                    raise NotImplementedError("Encryption not yet implemented")
                
                # Due to https://github.com/msgpack/msgpack-python/issues/99
                msg = msgpack.unpackb(body,encoding="utf-8")
                
                # No error catching, for better debugging
                self.registry.getObj(pid)._receive(msg)
                self.on_receive(pid,msg)
                self.sendEvent("peng3dnet:client.recv",{"pid":pid,"msg":msg})
                n+=1
        return n
    def process_forever(self):
        while self.run:
            # TODO: make interruptable
            self.process(wait=True,timeout=0.01)
    def process_async(self):
        self._process_thread = threading.Thread(name="peng3dnet process Thread",target=self.process_forever)
        self._process_thread.daemon = True
        self._process_thread.start()
    
    def close_connection(self,cid=None,reason=None):
        # not removed immediately to ensure that the reason is transmitted
        self.send_message("peng3dnet:internal.closeconn",{"reason":reason})
        self._mark_close = True
        self._close_reason = reason
    
    def join(self):
        self.stop()
        if self._run_thread is not None:
            self._run_thread.join()
        if self._process_thread is not None:
            self._process_thread.join()
    
    def close(self,reason=None):
        self.sendEvent("peng3dnet:client.close",{"reason":reason})
        try:
            sock.close()
        except Exception:
            pass
        try:
            with self._selector_lock:
                self.selector.unregister(sock)
        except Exception:
            pass
        if self.remote_state!=STATE_CLOSED:
            self.on_close(reason)
        self.remote_state = STATE_CLOSED
    
    # Server callbacks
    def on_handshake_complete(self):
        self.sendEvent("peng3dnet:client.handshakecomplete",{})
        self.remote_state = STATE_ACTIVE
    def on_connect(self):
        pass
    def on_close(self,reason=None):
        pass
    def on_receive(self,ptype,msg):
        pass
    def on_send(self,ptype,msg):
        pass
    
    def sendEvent(self,event,data):
        if self.cfg["net.events.enable"]:
            if isinstance(data,dict):
                data["peng"]=self.peng
                data["client"]=self
            self.peng.sendEvent(event,data)
