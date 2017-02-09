#!/usr/bin/env python2

from distutils.core import setup

setup(name='mLib',
      version='1.0',
      description='Library contains functions commonly used in malware research',
      author='Maciej Kotowicz',
      author_email='mak@lokalhost.pl',
      url='https://github.com/mak/mlib',
      package_dir = {'mlib':'src'},
      packages=['mlib','mlib.compression','mlib.crypto'],
      package_data = {'mlib':['so/*so']}
     )
