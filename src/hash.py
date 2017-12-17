import binascii
from mlib.bits import rol


def mlwr_hash(name):
    return rol7_hash(name)


def rol7_hash(name):
    x = 0
    for c in name:
        x = rol(x, 7)
        x = (x ^ ord(c)) & 0xff | x & 0xffffff00
    return x


def std_hash(name):
    x = 0
    for c in name:
        x = (rol(x, 19) + ord(c)) & 0xffffffff
    return x


def crc32_hash(name):
    return binascii.crc32(name) & 0xffffffff


def djb2_hash(name):
    x = 5381
    for c in name:
        x = ((x << 5) + x) + ord(c)
        x &= 0xffffffff
    return x


def sdbm_hash(name):
    x = 0
    for c in name:
        x = ord(c) + (x << 6) + (x << 16) - x
        x &= 0xffffffff
    return x
