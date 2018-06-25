#!/usr/bin/env python2

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def long_description():
    with open('README.rst') as f:
        d=f.read()
    return d

setup(name='mLib',
      version='1.2.4',
      description='Library contains functions commonly used in malware research',
      long_description=long_description(),
      author='Maciej Kotowicz',
      author_email='mak@lokalhost.pl',
      url='https://github.com/mak/mlib',
      package_dir={'mlib': 'src'},
      packages=['mlib', 'mlib.compression', 'mlib.crypto',
                'mlib.disasm', 'mlib.winapi', 'mlib.malware',
                'mlib.struct'],
      package_data={'mlib': ['so/*so']},
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: Public Domain',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2 :: Only',
          'Programming Language :: Assembly',
          'Programming Language :: C',
          'Topic :: Utilities'
      ])
