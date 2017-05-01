#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  registry.py
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

import threading

import bidict

from . import packet

class BaseRegistry(object):
    objtype = object
    def __init__(self,objtype=None):
        # Three types:
        # obj - Arbitrary Object
        # int - integer repr
        # str - string name/repr
        
        self.objtype = objtype if objtype is not None else self.objtype
        
        # Only two bidicts needed, optimized for int-obj conversion
        # int-obj conversion will be most common during packet parsing
        # str-obj/obj-str will be the slowest, due to indirect link
        # Conversion speeds:
        # int-int: 0 Lookups
        # int-obj: 1 Lookup
        # int-str: 1 Lookup
        # obj-int: 1 Lookup
        # obj-obj: 0 Lookups
        # obj-str: 2 Lookups
        # str-int: 1 Lookup
        # str-obj: 2 Lookups
        # str-str: 0 Lookups
        self.reg_int_obj = bidict.bidict()
        self.reg_int_str = bidict.bidict()
        
        self.nextid = 64 # allows for the first 64 IDs to be assigned manually
        self.idlock = threading.Lock()
    
    def getNewID(self):
        with self.idlock:
            n = self.nextid
            self.nextid+=1
            return n
    
    def register(self,obj,name,n=None):
        # int automatically generated
        if not isinstance(obj,self.objtype):
            raise TypeError("This registry only accepts objects of type %s"%self.objtype)
        
        if n is None: # Allows for overwriting the ID and essentially static IDs
            n = self.getNewID()
        
        self.reg_int_obj[n]=obj
        self.reg_int_str[n]=name
    def registerObject(self,obj,n=None):
        self.register(obj,obj.name,n)
    
    def deleteObj(self,obj):
        intid = self.getID(obj)
        del self.reg_int_obj[intid]
        del self.reg_int_str[intid]
    
    def getName(self,obj):
        if isinstance(obj,str):
            return obj
        elif isinstance(obj,int):
            return self.reg_int_str[obj]
        elif isinstance(obj,self.objtype):
            return self.reg_int_str[self.reg_int_obj.inv[obj]]
        else:
            raise TypeError("Cannot convert object of type %s to name"%type(obj))
    getStr = getName
    def getID(self,obj):
        if isinstance(obj,int):
            return obj
        elif isinstance(obj,str):
            return self.reg_int_str.inv[obj]
        elif isinstance(obj,self.objtype):
            return self.reg_int_obj.inv[obj]
        else:
            raise TypeError("Cannot convert object of type %s to ID"%type(obj))
    getInt = getID
    def getObj(self,obj):
        if isinstance(obj,self.objtype):
            return obj
        elif isinstance(obj,int):
            return self.reg_int_obj[obj]
        elif isinstance(obj,str):
            return self.reg_int_obj[self.reg_int_str.inv[obj]]
        else:
            raise TypeError("Cannot convert object of type %s to Obj"%type(obj))
    
    def getAll(self,obj):
        return self.getObj(obj),self.getID(obj),self.getName(obj)
    
    def __getitem__(self,item):
        return self.getObj(item)

class PacketRegistry(BaseRegistry):
    objtype = packet.Packet
