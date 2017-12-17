__all__ = ['unpack', 'decompress']

# this is a standalone single-file merge of aplib compression and decompression
# taken from my own library Kabopan http://code.google.com/p/kabopan/
# (no other clean-up or improvement)

# Ange Albertini, BSD Licence, 2007-2011

# from kbp\comp\_lz77.py  ##################################################


def find_longest_match(s, sub):
    """returns the number of byte to look backward and the length of byte to copy)"""
    if sub == "":
        return 0, 0
    limit = len(s)
    dic = s[:]
    l = 0
    offset = 0
    length = 0
    first = 0
    word = ""

    word += sub[l]
    pos = dic.rfind(word, 0, limit + 1)
    if pos == -1:
        return offset, length

    offset = limit - pos
    length = len(word)
    dic += sub[l]

    while l < len(sub) - 1:
        l += 1
        word += sub[l]

        pos = dic.rfind(word, 0, limit + 1)
        if pos == -1:
            return offset, length
        offset = limit - pos
        length = len(word)
        dic += sub[l]
    return offset, length

# from _misc.py ###############################


def int2lebin(value, size):
    """ouputs value in binary, as little-endian"""
    result = ""
    for i in xrange(size):
        result = result + chr((value >> (8 * i)) & 0xFF)
    return result


def modifystring(s, sub, offset):
    """overwrites 'sub' at 'offset' of 's'"""
    return s[:offset] + sub + s[offset + len(sub):]


def getbinlen(value):
    """return the bit length of an integer"""
    result = 0
    if value == 0:
        return 1
    while value != 0:
        value >>= 1
        result += 1
    return result


class _bits_decompress():
    """bit machine for variable-sized auto-reloading tag decompression"""

    def __init__(self, data, tagsize):
        self.__curbit = 0
        self.__offset = 0
        self.__tag = None
        self.__tagsize = tagsize
        self.__in = data
        self.out = ""

    def getoffset(self):
        """return the current byte offset"""
        return self.__offset

#    def getdata(self):
#        return self.__lzdata

    def read_bit(self):
        """read next bit from the stream, reloads the tag if necessary"""
        if self.__curbit != 0:
            self.__curbit -= 1
        else:
            self.__curbit = (self.__tagsize * 8) - 1
            self.__tag = ord(self.read_byte())
            for i in xrange(self.__tagsize - 1):
                self.__tag += ord(self.read_byte()) << (8 * (i + 1))

        bit = (self.__tag >> ((self.__tagsize * 8) - 1)) & 0x01
        self.__tag <<= 1
        return bit

    def is_end(self):
        return self.__offset == len(self.__in) and self.__curbit == 1

    def read_byte(self):
        """read next byte from the stream"""
        if type(self.__in) == str:
            result = self.__in[self.__offset]
        elif hasattr(self.__in, 'read'):
            result = self.__in.read(1)
        self.__offset += 1
        return result

    def read_fixednumber(self, nbbit, init=0):
        """reads a fixed bit-length number"""
        result = init
        for i in xrange(nbbit):
            result = (result << 1) + self.read_bit()
        return result

    def read_variablenumber(self):
        """return a variable bit-length number x, x >= 2

        reads a bit until the next bit in the pair is not set"""
        result = 1
        result = (result << 1) + self.read_bit()
        while self.read_bit():
            result = (result << 1) + self.read_bit()
        return result

    def read_setbits(self, max_, set_=1):
        """read bits as long as their set or a maximum is reached"""
        result = 0
        while result < max_ and self.read_bit() == set_:
            result += 1
        return result

    def back_copy(self, offset, length=1):
        for i in xrange(length):
            self.out += self.out[-offset]
        return

    def read_literal(self, value=None):
        if value is None:
            self.out += self.read_byte()
        else:
            self.out += value
        return False


# from kbp\comp\aplib.py ###################################################
"""
aPLib, LZSS based lossless compression algorithm

Jorgen Ibsen U{http://www.ibsensoftware.com}
"""


def lengthdelta(offset):
    if offset < 0x80 or 0x7D00 <= offset:
        return 2
    elif 0x500 <= offset:
        return 1
    return 0


class a_decompress(_bits_decompress):
    def __init__(self, data):
        _bits_decompress.__init__(self, data, tagsize=1)
        self.__pair = True    # paired sequence
        self.__lastoffset = 0
        self.__functions = [
            self.__literal,
            self.__block,
            self.__shortblock,
            self.__singlebyte]
        return

    def __literal(self):
        self.read_literal()
        self.__pair = True
        return False

    def __block(self):
        b = self.read_variablenumber()    # 2-
        if b == 2 and self.__pair:    # reuse the same offset
            offset = self.__lastoffset
            length = self.read_variablenumber()    # 2-
        else:
            high = b - 2    # 0-
            if self.__pair:
                high -= 1
            offset = (high << 8) + ord(self.read_byte())
            length = self.read_variablenumber()    # 2-
            length += lengthdelta(offset)
        self.__lastoffset = offset
        self.back_copy(offset, length)
        self.__pair = False
        return False

    def __shortblock(self):
        b = ord(self.read_byte())
        if b <= 1:    # likely 0
            return True
        length = 2 + (b & 0x01)    # 2-3
        offset = b >> 1    # 1-127
        self.back_copy(offset, length)
        self.__lastoffset = offset
        self.__pair = False
        return False

    def __singlebyte(self):
        offset = self.read_fixednumber(4)  # 0-15
        if offset:
            self.back_copy(offset)
        else:
            self.read_literal('\x00')
        self.__pair = True
        return False

    def do(self):
        """returns decompressed buffer and consumed bytes counter"""
        self.read_literal()
        while True:
            if self.__functions[self.read_setbits(3)]():
                break
        return self.out, self.getoffset()


# end of Kabopan
import StringIO
import ctypes

from mlib.misc import load_dll
aPLIB = load_dll('so/_aplib.so')


def unpack(data, s=0):
    cin = ctypes.c_buffer(data)
    cout = ctypes.c_buffer(s if s else len(data) * 20)
    n = aPLIB.aP_depack(cin, cout)
    return cout.raw[:n]


def decompress(d, s):
    try:
        r = a_decompress(StringIO.StringIO(d)).do()[0]
    except IndexError:
        r = unpack(d, s)
    return r
