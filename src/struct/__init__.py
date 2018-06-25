import sys
import struct as st
import ctypes

if st == sys.modules[__name__]:
    del sys.modules['struct']
    st = __import__('struct')


uqword = lambda d, off=0: st.unpack_from('<Q',d,off)[0]
udword = lambda d, off=0: st.unpack_from('<I',d,off)[0]
uword  = lambda d, off=0: st.unpack_from('<H',d,off)[0]
ubyte  = lambda d ,off=0: st.unpack_from('<B',d,off)[0]

class Structure(ctypes.Structure):

    _blacklist_ = []

    @classmethod
    def sizeof(self):
        return ctypes.sizeof(self)
    
    @classmethod
    def parse(self,data):
        return self.from_buffer_copy(data)

    @classmethod
    def new(self):
        return self.parse("\x00"*self.sizeof())

    @classmethod
    def from_cstruct(self,code):
        try:
            import pycparser
            from .cparse import parse_cstruct
            return parse_cstruct(code,self)
        
        except ImportError:
            raise Exception('i need pycparser for it')
    
    def pack(self):
        return buffer(self)[:]
    
    def as_dict(self):
        ret = {}
        for field, _ in self._fields_:
            if field in self._blacklist_:
                continue
            
            value = getattr(self, field)
            if isinstance(value, Structure):
                ret[field] = value.as_dict()
            elif hasattr(value, "value"):
                ret[field] = value.value
            elif hasattr(value, "__getitem__"):
                ret[field] = value[:]
            else:
                ret[field] = value
        return ret
