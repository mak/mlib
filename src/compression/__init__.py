import ctypes
import struct

from . import lznt1 as _lznt1
from . import aplib as _aplib
from mlib.misc import load_dll


class lznt1:
    @classmethod
    def decompress(cls, data):
        return _lznt1.decompress_data(data)


class lzmat:
    LIB = load_dll("so/_lzmat.so")

    @classmethod
    def _hash(d):
        return cls.LIB.hash(ctypes.c_buffer(d), ctypes.c_uint(len(d)))

    @classmethod
    def decompress(cls, d):
        dec_size = ctypes.c_uint(struct.unpack("I", d[:4])[0])
        out = ctypes.c_buffer(dec_size.value)
        cls.LIB.lzmat_decode(out, ctypes.byref(dec_size), d[4:], len(d[4:]))
        return out.raw


class gzip:

    @classmethod
    def decompress(cls, d):
        if not d.startswith("\x1f\x8b\x08\x00"):
            return d

        import subprocess
        p = subprocess.Popen(['gunzip', '-', '-c', '-n'], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        r, _ = p.communicate(d)
        return r

    def compress(cls, d):
        import subprocess
        p = subprocess.Popen(['gzip', '-', '-c', '-n'],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        r, _ = p.communicate(d)
        return r


class aplib:

    @classmethod
    def decompress(cls, data, s=0):
        return _aplib.decompress(data, s)
