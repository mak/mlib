import hashlib
import operator
import itertools
import sys
import struct

from ctypes import cdll, c_buffer
from Crypto.Cipher import AES
from Crypto.Cipher import ARC4 as RC4
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from mlib.misc import load_dll
from mlib.bits import rol

from . import rc6 as _rc6
from . import rc2 as _rc2
from . import spritz as _spritz
from . import rabbit as _rabbit

def chunks(l, n): return [l[x: x + n] for x in xrange(0, len(l), n)]


def rsa(k):
    return RSA.importKey(k)


def rsa_pkcs(k):
    return PKCS1_v1_5.new(rsa(k))


def rsa_new_key(n=1024):
    return RSA.generate(n)


def rsa_new_pkcs(n=1024):
    return PKCS1_v1_5.new(rsa_new_key(n))


class rc2:

    RC2_BLOCK_SIZE = 8
    MODE_ECB = 0
    MODE_CBC = 1
    PADDING_PKCS5 = 1

    @classmethod
    def decrypt(cls, d, key, mode, IV=None, padding=None):
        return _rc2(key).decrypt(d, mode, IV, padding)

    @classmethod
    def encrypt(cls, d, key, mode, IV=None, padding=None):
        return _rc2(key).decrypt(d, mode, IV, padding)


class aes:

    @classmethod
    def decrypt(cls, d, k=None, _xor=None, mode='ecb', *rest):
        if not k:
            k = cls.key

        mode = getattr(AES, 'MODE_' + mode.upper())
        clean = AES.new(k, mode, *rest).decrypt(d)
        if _xor:
            return xor(clean, _xor)
        return clean


class rc4:

    @classmethod
    def decrypt(cls, data, key=None, derive_key=None, use_sbox=False, xor=None, mod1=0, mod2=0):

        if not key:
            key = cls.key

        if derive_key:
            key = derive_key(key)

        if not use_sbox:
            cip = RC4.new(key)
            return cip.decrypt(data)

        box = map(ord, key)
        x = 0
        y = 0
        out = []
        idx = 0
        for byt in data:
            x = (x + 1 + mod1) % 256
            y = (y + box[x] + mod2) % 256
            box[x], box[y] = box[y], box[x]
            byt = ord(byt) ^ box[(box[x] + box[y]) % 256]
            if xor:
                byt ^= ord(xor[idx % len(xor)])
            idx += 1
            out.append(chr(byt))

        return ''.join(out)

    @classmethod
    def ms_derive_key(cls, key, hash):
        k = getattr(hashlib, hash)(key).digest()[:5]
        return k

    encrypt = decrypt

def visEncry(datA):
    i = len(datA) - 1
    ret = map(ord, (datA))
    for idx in range(1, len(datA)):
        ret[idx] ^= ret[idx - 1]
    return ''.join(map(chr, ret))


def visDecry(datA):
    i = len(datA) - 1
    ret = map(ord, (datA))
    for idx in range(len(datA) - 1, 0, -1):
        ret[idx] ^= ret[idx - 1]
    return ''.join(map(chr, ret))


def rolling_xor(d, key, rl=8, off=0, add_index=False, xor_index=False):
    r = []
    for i, c in enumerate(d):
        a = ord(c) ^ key ^ (i if xor_index else 0)
        r.append(chr(a & 0xff))

        key = rol(key, rl) + off
        if add_index:
            key += i
    return ''.join(r)


def xor(x, y, xor_index=False):
    return ''.join(map(lambda a: chr(ord(a[1][0]) ^ ord(a[1][1]) ^ (a[0] if xor_index else 0)), enumerate(zip(x, itertools.cycle(y)))))


class xtea:

    @staticmethod
    def xtea_decrypt_block(key, block, n=32, endian="!"):
        v0, v1 = struct.unpack(endian + "2L", block)
        k = struct.unpack(endian + "4L", key)
        delta, mask = 0x9e3779b9L, 0xffffffffL
        sum = (delta * n) & mask
        for round in range(n):
            v1 = (v1 - (((v0 << 4 ^ v0 >> 5) + v0) ^
                        (sum + k[sum >> 11 & 3]))) & mask
            sum = (sum - delta) & mask
            v0 = (v0 - (((v1 << 4 ^ v1 >> 5) + v1)
                        ^ (sum + k[sum & 3]))) & mask
        return struct.pack(endian + "2L", v0, v1)

    @staticmethod
    def xtea_encrypt_block(key, block, n=32, endian="!"):
        v0, v1 = struct.unpack(endian + "2L", block)
        k = struct.unpack(endian + "4L", key)
        sum, delta, mask = 0L, 0x9e3779b9L, 0xffffffffL
        for round in range(n):
            v0 = (v0 + (((v1 << 4 ^ v1 >> 5) + v1)
                        ^ (sum + k[sum & 3]))) & mask
            sum = (sum + delta) & mask
            v1 = (v1 + (((v0 << 4 ^ v0 >> 5) + v0) ^
                        (sum + k[sum >> 11 & 3]))) & mask
        return struct.pack(endian + "2L", v0, v1)

    @staticmethod
    def xtea_worker(f, data):
        _len = len(data)
        assert len(data) % 8 == 0
        return ''.join(map(f, chunks(data, 8)))

    @classmethod
    def decrypt(cls, data, xkey):
        return cls.xtea_worker(lambda c: cls.xtea_decrypt_block(xkey, c), data)

    @classmethod
    def encrypt(cls, data, xkey):
        return cls.xtea_worker(lambda c: cls.xtea_encrypt_block(xkey, c), data)


class rc6:

    @classmethod
    def decrypt(cls, d, k, typ='sbox',**kwargs):
        if typ == 'str':
            rc = _rc6.RC6(k,**kwargs)
            def ciph(d, k): return rc.decrypt(d)
        else:
            if type(k) == str:
                k = struct.unpack('I' * (len(k) / 4), k)

            def ciph(d, k): return _rc6.RC6('a' * 16).decrypt(d, k)
                
        r = []
        for i in range(0, len(d) >> 4):
            r.append(ciph(d[i * 16:(i + 1) * 16], k))
        return ''.join(r)

    @classmethod
    def encrypt(cls, d, k, typ='sbox',**kwargs):
        if typ == 'str':
            rc = _rc6.RC6(k,**kwargs)
            def ciph(d, k): return rc.encrypt(d)
        else:
            if type(k) == str:
                k = struct.unpack('I' * (len(k) / 4), k)

            def ciph(d, k): return _rc6.RC6('a' * 16).encrypt(d, k)
                
        r = []
        for i in range(0, len(d) >> 4):
            r.append(ciph(d[i * 16:(i + 1) * 16], k))
        return ''.join(r)


class spritz:

    _class = _spritz.Spritz(op=operator.xor)

    @staticmethod
    def mk_args(data, key):
        xdata = data
        xkey = key
        if type(data) != bytearray:
            xdata = bytearray(xdata)

        if type(xkey) != bytearray:
            xkey = bytearray(xkey)
        return xdata, xkey

    @classmethod
    def decrypt(cls, data, key):
        data, key = cls.mk_args(data, key)
        return str(cls._class.decrypt(key, data))

    encrypt = decrypt

class serpent:
    LIB = load_dll('so/_serpent.so')
    BLOCK_SIZE = 16

    @staticmethod
    def align_size(n):
        return (n + (serpent.BLOCK_SIZE - 1)) & (~(serpent.BLOCK_SIZE - 1))

    @classmethod
    def decrypt(cls, data, key):
        clen = cls.align_size(len(data))
        ckey = c_buffer(key)
        cin = c_buffer(data)
        cout = c_buffer(clen)
        cls.LIB.decrypt(cin, clen, ckey, cout)
        return cout.raw

    @classmethod
    def encrypt(cls, data, key):
        clen = cls.align_size(len(data))
        data = data.ljust(clen, "\x00")
        ckey = c_buffer(key)
        cin = c_buffer(data)
        cout = c_buffer(clen)
        cls.LIB.encrypt(cin, clen, ckey, cout)
        return cout.raw



class rabbit:
    
    @classmethod
    def encrypt(cls,data,key,iv=None):
        return _rabbit.Rabbit(key,iv or '').crypt(data)

    decrypt = encrypt
