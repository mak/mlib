import types
import sys
import os
import struct
from StringIO import StringIO


if 'struct' in sys.modules:
    del sys.modules['struct']
    st = __import__('struct')


def get_size(klass):
    import ctypes
    f = getattr(klass, 'sizeof', lambda: ctypes.sizeof(klass))
    return f()


# sys._getframe(1).f_code.co_name
class M(object):

    TRANSL = {'byte': ('B', 1), 'word': ('H', 2),
              'dword': ('I', 4), 'qword': ('Q', 8)}

    def __init__(self, d, end_fmt=''):
        self._len = len(d)
        self.b = StringIO(d)

    def _get_bytes(self, fmt, s, off):
        return st.unpack(fmt, self.read(off, s) if off else self.read(s))[0]

    def skip(self, n):
        self.b.seek(n, os.SEEK_CUR)

    def unskip(self, n):
        self.b.seek(-n, os.SEEK_CUR)

    def read(self, a0, a1= None):
        r = None
        if a1 is None:
            r = self.b.read(a0)
        else:
            r = self.read_at(a0,a1)
        return r
    
    def read_at(self, off, n):
        old_l = self.b.tell()
        self.b.seek(off, os.SEEK_SET)
        r = self.b.read(n)
        self.b.seek(old_l, os.SEEK_SET)
        return r

    def read_struct_at(self, klass, at):
        d = self.read_at(at, get_size(klass))
        return klass.parse(d)

    def read_struct(self, klass):
        d = self.read(get_size(klass))
        return klass.parse(d)

    # def bytes(self,t):
    #     s=  self.dword()
    #     return self.read
    def __len__(self):
        return self._len

    def __getattr__(self, name):
        at = False
        if name.endswith('_at'):
            name = name[:-3]

        if name in M.TRANSL:
            f, s = M.TRANSL[name]
            return lambda off = None: self._get_bytes(f, s, off)



if __name__ == '__main__':
    m = M(sys.stdin.read())
    print dir(m)
    print m.word, m.byte
#    print m.byte()
    print m.dword()
#    print m.word_at(0)
