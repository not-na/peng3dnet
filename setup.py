#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#  
#  Copyright 2017-2022 notna <notna@apparat.org>
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

# Distribution command:
# python setup.py sdist bdist bdist_egg bdist_wheel
# outside venv:
# twine upload dist/*

import os
import runpy

ver = runpy.run_path(os.path.join("peng3dnet", "version.py"))

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    longdesc = open("README.rst", "r").read()
except Exception:
    longdesc = "Networking Library for Peng3d"

setup(name='peng3dnet',
      version=ver["VERSION"],
      description="Networking Library for Peng3d", # from the github repo
      long_description=longdesc,
      author="notna",
      author_email="notna+gh@apparat.org",
      url="https://github.com/not-na/peng3dnet",
      packages=['peng3dnet',"peng3dnet.packet","peng3dnet.ext"],
      install_requires=["msgpack~=1.0.0","bidict>=0.19.0"],
      provides=["peng3dnet"],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      classifiers=[
        "Development Status :: 5 - Production/Stable",

        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",

        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Telecommunications Industry",

        "License :: OSI Approved",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",

        "Operating System :: OS Independent",

        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",

        "Topic :: Communications",
        "Topic :: Internet",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        
        ],
      )
