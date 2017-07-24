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

__all__ = [
    "BaseRegistry",
    "PacketRegistry",
    ]

import threading

try:
    import bidict
except ImportError:
    HAVE_BIDICT = False
else:
    HAVE_BIDICT = True

from . import packet

class BaseRegistry(object):
    """
    Basic registry class.
    
    Supports smart conversions between the integer, string and generic object representation of a registered entity.
    
    Optionally allows for automatic and threadsafe integer ID generation.
    
    Requires :py:mod:`bidict` to be installed and available.
    
    ``objtype`` may be used to override the class attribute of the same name per instance.
    
    Instances of this class also support dictionary-style access to their data,
    e.g. ``reg[val]`` will always return the object representation of the value,
    see :py:meth:`getObj()` for details.
    """
    objtype = object
    """
    Class attribute defining what type should be used to check for the generic object representation using :py:func:`isinstance()`\ .
    """
    def __init__(self,objtype=None):
        if not HAVE_BIDICT:
            raise RuntimeError("Bidict is required for usage of BaseRegistry")
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
        """
        Generates a new ID.
        
        Currently, all IDs are increasing from a fixed starting point, by default ``64``\ .
        """
        with self.idlock:
            n = self.nextid
            self.nextid+=1
            return n
    
    def register(self,obj,name,n=None):
        """
        Registers a relation between an object, its string representation and its integer representation.
        
        If ``n`` is not given, :py:meth:`getNewID()` will be used to generate it.
        
        Trying to register an already registered object may cause various kinds of corruptions on internal storages.
        
        Trying to register an object that is not of the type specified in :py:attr:`objtype` will result in an :py:exc:`TypeError`\ .
        """
        # int automatically generated
        if not isinstance(obj,self.objtype):
            raise TypeError("This registry only accepts objects of type %s"%self.objtype)
        
        if n is None: # Allows for overwriting the ID and essentially static IDs
            n = self.getNewID()
        
        self.reg_int_obj[n]=obj
        self.reg_int_str[n]=name
    def registerObject(self,obj,n=None):
        """
        Same as :py:meth:`register()`\ , but extracts the string representation from the object's ``name`` attribute.
        """
        self.register(obj,obj.name,n)
    
    def deleteObj(self,obj):
        """
        Removes an object from the internal registry.
        
        ``obj`` may be any of the three representations of an object.
        """
        intid = self.getID(obj)
        del self.reg_int_obj[intid]
        del self.reg_int_str[intid]
    
    def getName(self,obj):
        """
        Converts the given value to its string representation.
        
        This method accepts either strings, integers or objects of type :py:attr:`objtype`\ .
        
        :py:meth:`getStr()` may be used as an alias to this method.
        """
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
        """
        Converts the given value to its integer representation.
        
        This method accepts either strings, integers or objects of type :py:attr:`objtype`\ .
        
        :py:meth:`getInt()` may be used as an alias to this method.
        """
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
        """
        Converts the given value to its object representation.
        
        This method accepts either strings, integers or objects of type :py:attr:`objtype`\ .
        """
        if isinstance(obj,self.objtype):
            return obj
        elif isinstance(obj,int):
            return self.reg_int_obj[obj]
        elif isinstance(obj,str):
            return self.reg_int_obj[self.reg_int_str.inv[obj]]
        else:
            raise TypeError("Cannot convert object of type %s to Obj"%type(obj))
    
    def getAll(self,obj):
        """
        Returns a three-tuple of form ``(getObj(obj),getID(obj),getName(obj))``\ .
        """
        return self.getObj(obj),self.getID(obj),self.getName(obj)
    
    def __getitem__(self,item):
        return self.getObj(item)

class PacketRegistry(BaseRegistry):
    """
    Subclass of :py:class:`BaseRegistry` customized for storing :py:class:`~peng3dnet.packet.Packet` instances and instances of subclasses.
    """
    objtype = packet.Packet
