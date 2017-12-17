import random as _rnd
import string


def rstring(n=0, rng=(4, 10)):
    n = n if n else _rnd.randint(*rng)
    return ''.join([_rnd.choice(string.ascii_letters) for _ in xrange(n)])


def rint32():
    return _rnd.randint(0, 0xffffffff)


def rint16():
    return _rnd.randint(0, 0xffff)


def rword():
    return rint16()


def rint8():
    return _rnd.randint(0, 0xff)


def rmax(n):
    return _rnd.randint(0, n)


def rip():
    return '%d.%d.%d.%d' % (rint8(), rint8(), rint8(), rint8())


class LCG(object):
    mul = 0
    add = 0

    def __init__(self):
        self.seed = 0

    @property
    def rnd(self):
        self.seed = (((self.mul * self.seed) & 0xFFFFFFFF) +
                     self.add) & 0xFFFFFFFF
        return self.seed

    def choose(self, l):
        return l[self.rnd % len(l)]

    def xor(self, data):
        return ''.join([chr((self.rnd ^ ord(c)) & 0xff) for c in data])


def rbytes(n):
    with open('/dev/urandom') as f:
        r = f.read(n)
    return r


class LsaRandom(LCG):
    mul = 0x19660D
    add = 0x3C6EF35F
