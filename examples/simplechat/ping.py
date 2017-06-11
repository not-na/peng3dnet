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

import pprint

import peng3dnet

def main(args):
    if len(args)==2:
        addr = args[1]
    else:
        addr = input("Server address:")
    
    print("Pinging server...")
    data = peng3dnet.ext.ping.pingServer(addr=addr)
    print("Done")
    
    print("Latency of %.2fms"%(data["delay"]*1000))
    print("Raw data:")
    pprint.pprint(data)
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
