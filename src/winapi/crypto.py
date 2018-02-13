import sys
import enum
import ctypes as c

from mlib.misc import E
from mlib.memory import M
from mlib.rnd import rint32
from mlib.struct import Structure

import struct
import mlib.crypto as cr
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

__all__ = ["export_key", "import_key"]


class BTYPE(E):
    SIMPLEBLOB = 1
    PUBLICKEYBLOB = 6
    PRIVATEKEYBLOB = 7
    PLAINTEXTKEYBLOB = 8
    OPAQUEKEYBLOB = 9
    PUBLICKEYBLOBEX = 10
    SYMMETRICWRAPKEYBLOB = 11
    KEYSTATEBLOB = 12


class BLOBHEADER(Structure):
    _fields_ = [
        ('bType', c.c_ubyte),
        ('bVersion', c.c_ubyte),
        ('reserved', c.c_ushort),
        ('algid', c.c_uint),
    ]


def make_enc_key(pk):
    if type(pk) == str:
        pk = import_key(pk)
    elif type(pk) == dict:
        if 'd' in pk:
            pk = RSA.construct((long(pk['n']), long(pk['e']), long(pk['d'])))
        else:
            pk = RSA.construct((long(pk['n']), long(pk['e'])))

    if pk.__class__.__name__ != 'PKCS115_Cipher':
        pk = PKCS1_v1_5.new(pk)
    return pk


class UnsuportedKey(Exception):
    pass


class WrongKeyType(Exception):
    pass


class WrongPrivKey(Exception):
    pass


class KRYPTO(object):

    types = {
        0x0000660e: 'aes',
        0x0000660f: 'aes',
        0x00006610: 'aes',
        0x00006602: 'rc2',
        0x00006801: 'rc4',
        0x0000a400: 'rsa',
        'rc4': 0x00006801,
        'rc2': 0x00006602,
        'aes128': 0x0000660e,
        'aes192': 0x0000660f,
        'aes256': 0x00006610,
        'rsa': 0x0000a400,
    }

    def mk_header(self, t):

        hdr = BLOBHEADER()
        hdr.bType = getattr(BTYPE, self.__class__.__name__).value
        hdr.bVersion = 2
        hdr.reserved = 0
        hdr.algid = self.types[t]
        return hdr

    def get_cipher(self, hdr):
        return getattr(cr, self.types[hdr.algid], None)

    def parse(self, m, **args):
        raise NotImplementedError()

    def export(self, m, **args):
        raise NotImplementedError()


class OPAQUEKEYBLOB(KRYPTO):
    pass


class PUBLICKEYBLOBEX(KRYPTO):
    pass


class SYMMETRICWRAPKEYBLOB(KRYPTO):
    pass


class KEYSTATEBLOB(KRYPTO):
    pass


class SIMPLEBLOB(KRYPTO):

    def parse(self, m, **args):

        assert m.read(4) == '\x00\xa4\x00\x00'
        enckey = m.read(256)[::-1]
        if 'privkey' in args:
            sent = rint32()
            pk = make_enc_key(args['privkey'])
            r = pk.decrypt(enckey, sent)
            if r == sent:
                raise WrongPrivKey

        else:
            r = enckey
        return r

    def export(self, data, **args):
        r = '\x00\xa4\x00\x00'
        if 'pubkey' in args:
            pk = make_enc_key(args['pubkey'])
            r += pk.encrypt(data)[::-1]
        else:
            m = 128
            if len(data) > 128:
                m = 256
            r += data.ljust(m, "\x00")[::-1]
        return r


class PLAINTEXTKEYBLOB(KRYPTO):

    def parse(self, m, **args):
        size = m.dword()
        return m.read(size)

    def export(self, data, **k):
        return struct.pack('I', len(data)) + data


class PUBLICKEYBLOB(KRYPTO):

    magic = 'RSA1'

    def chk_magic(self, m):
        assert m.read(4) == self.magic

    def get_int(self, b):
        return long(self.mem.read(self.bits / b)[::-1].encode('hex'), 16)

    def pack_int(self, n, b):
        return hex(n)[2:].strip('L').decode('hex').ljust(self.bits / b, "\x00")[::-1]

    def check_key(self, data):
        if type(data) == dict and 'n' in data and 'e' in data:
            e = data['e']
            n = data['n']
            self.bits = len(hex(n)[2:].strip('L')) * 8 / 2
        else:
            raise WrongKeyType

    def parse(self, m, **args):
        self.chk_magic(m)
        self.mem = m
        self.bits = m.dword()
        pexp = m.dword()
        return {'e': pexp, 'n': self.get_int(8)}

    def export(self, data, **args):
        self.check_key(data)
        r = self.magic
        r += struct.pack('II', self.bits, e)
        r += self.pack_int(n, 8)
        return r

    def make_key(self, _, key):
        return RSA.construct((key['n'], long(key['e'])))


class PRIVATEKEYBLOB(PUBLICKEYBLOB):

    magic = 'RSA2'

    def check_key(self, data):
        super(PRIVATEKEYBLOB, self).check_key(data)
        if 'd' not in data:
            raise WrongKeyType

    def parse(self, m, **args):

        key = super(PRIVATEKEYBLOB, self).parse(m, **args)
        key['p1'] = self.get_int(16)
        key['p2'] = self.get_int(16)
        key['exp1'] = self.get_int(16)
        key['exp2'] = self.get_int(16)
        key['coeff'] = self.get_int(16)
        key['d'] = self.get_int(8)
        return key

    def export(self, data, **args):
        self.check_key(data)
        key = super(PRIVATEKEYBLOB, self).export(data, **args)
        key += self.pack_int(data.get('p1', 0), 16)
        key += self.pack_int(data.get('p2', 0), 16)
        key += self.pack_int(data.get('exp1', 0), 16)
        key += self.pack_int(data.get('exp2', 0), 16)
        key += self.pack_int(data.get('coeff', 0), 16)
        key += self.pack_int(data.get('d', 0), 8)
        return key

    def make_key(self, _, key):
        return RSA.construct((key['n'], long(key['e']), key['d']))


def import_key(data, **kwargs):

    m = M(data)
    hdr = m.read_struct(BLOBHEADER)

    e = BTYPE.from_val(hdr.bType)
    if not e:
        raise WrongKeyType

    obj = getattr(sys.modules[__name__], e.name)()
    c = obj.get_cipher(hdr)
    if not c:
        raise UnsuportedKey

    key = obj.parse(m, **kwargs)
    if kwargs.get('dump_key', None) is True:
        return key
    elif hasattr(obj, 'make_key'):
        return obj.make_key(c, key, **kwargs)
    else:
        c.key = key
    return c


def export_key(type, key, **kwargs):

    if '_' in type:
        alg, mod = type.split('_')
    else:
        alg = type
        mod = None

    if mod == 'enc' and alg in ('rc2', 'rc4', 'aes'):
        obj = SIMPLEBLOB()
    elif alg in ('rc2', 'rc4', 'aes'):
        obj = PLAINTEXTKEYBLOB()

    elif mod == 'priv' and alg == 'rsa':
        obj = PRIVATEKEYBLOB()
    elif alg == 'rsa':
        obj = PUBLICKEYBLOB()

    else:
        raise WrongKeyType

    if type == 'aes':
        type = 'aes%d' % (len(data) * 8)

    r = obj.mk_header(alg).pack()
    r += obj.export(key, **kwargs)
    return r


if __name__ == '__main__':
    # some test and examples...
    pkey = '\x07\x02\x00\x00\x00\xa4\x00\x00RSA2\x00\x04\x00\x00\x01\x00\x01\x00\xb1O\x1f\xbe\xcaE\xadoe\x1a`V\x10.\xddr3\xcfwI_\xf0-\xe8T\xd8<3x\x03)\xc6\xaeL\xb0\xe1y]P\x1d\xd6\xa4\x84\x94\xc3|R\xac]\x9f\xb1W\xb9>\x17\x14\x98\xc7\xda\x8e\x8c\xb2y!z\x85\x8a>b\x02\xdf\x9e\xc8RO\xcd\xff\x8f]\xca;d\xd7\x82\'\xf8wqX\xa2\xa8\x82\xe5\xdd\x94\xe7\xc6\xa2\xb8\xb2\x89\xea<r\xbe$`*\x18\x18\xfaG6\xfet6Vb\xde93B\xf5\xbe\x85R\xba\xbf\xfb\x9f\xb2\x1bX\x05\x17\x7f\xf8\xd8\xdeq\x85P\x96\xde\xe2\xbd\xaa|w\xff`\xb33>y \xbd\xd76f\xf0\xe3\xd4\ng\xd0_\xc0\t:\xafk\xec\xb5\x01\xfe\xd4\xb9\x0c\xbb0\xb4\x96]\x0c9\xa9\x8e\x16\xc6\x7f\xf6C\x83\xe6!\x1cS\xd8\xbd\x19g\x18\xfe\x0f\x95pVA\xdb8\xe1\x99R$\x9e\xfc\xd3\xebC\xbb\x13\xf7f}M}\xc8x!\x98\xe4\x011\xb1\xed\x97}\xb7:\xfc\x88\xb0\xde\xd30\x06\xcc\x90\xdaW\xdd\xaa\x1d\x1e\xc7\x9f\x95yTa\xf5u\x996\x0c\xc8\x91\xd7\xcfw\xbc\x97\xee\x13\xd4p\x0e6\xba\x85L\x9c\\\xd8\xe3\xf5\x8d_\t\x81\x8a\xde\xbb\x15\x18\xee\xfe\x0e\x0fqi\xbd\xc7\x16\xab\x9e\xc9\xd9L\x82*\xfc0>#J\x1b\x1a^M\x8f\x8dF)\xd8\xa7I\xbb#z\x05\x93\xf5\xa2\x8a\xd4\x9e\xd8\t \x91\x9e\xa0\xae}\xc3\x95q\x9e.\xb8\xac\x9az(\xa8l*#\x963~\xdcX\x05X\x99\xdd\xddsC\xde\x17t}\xb3\xfdX\x9d3-^\x8a5\xaf\xbe\xc2\x8c\x1b\xf9\xab\xec\xef1,\xde\x15I~\x8e/[y&[\xce_k\x02\xf2N\x07\x0e/\xd4\x18\xfc\x133\xea\xe5\xa6/\x12\xce\xe1\xf4\xce\xba\x05\xb6c\xbb\'\x87\xce\x9d\xacD\x1b\xb1\x13\xa2\xb5\xde=@!Q\xc2+\xb8\x1bW\tbxu\x8a\xb8N]\xe3\x97\x9a\x974\xac\n\x1c(\xc4iIpyG\x04\x8e\xb6\xcd\n\xa8\xed!\xdbo`\'\xefb\x12^\xdc\x8ac_?\xdd\xb6\x15\xe2{\xfa\xc9\xd7\x82\xf78)VS_\x1b\x080?NQ\x92\x9e\xe5t\x9b\x02\xcf\xbb\x93\xe9\x10\x005_:$\x8a~\xeb\x94\x82*\xce r\x05\x96<\x86\xe7(\x9e,\xed\xfb?\xde\x8c\xbb\xb5D\x93v\xf8\x99J\x11\xa3\xd9\xc2F\x88B2" '
    key = import_key(pkey)
    key = make_enc_key(pkey)

    smplk = "\x01\x02\x00\x00\x01h\x00\x00\x00\xa4\x00\x00\xb8\xa7\x92i5\xed+x\x080\x884x\xdf\xad\xa7\x03\xe6\xa2I\xefa\xe2\xf2\xa4\xe9Xu\xb6a\xd4s\x06J\x198\r<\xe0\x13\x04\x89\xfd\x1d\x96(\xad\xb9\xec\x9f\x82,\xc0\xb9\xaf4=\xdaR\xd7?\x9fFVF\xab\x9e\xc8\x0c\xc0\x81\xa2\xec\xc7\xee&\xa7qNH\x1e!\x1a\xc1\xaa\x81\xdcjQ\x88\xebv\xb7-\xeaQ<\xbe\xa1SR\xbd?ZG\xf1\x08\x8b\xf8\xd9\xe5\r$\x884&\xa0\xf7\xf3\xdd\xb5\x82;\x9b\xa5\xd5\xac\xa2"

    smplk2 = '\x01\x02\x00\x00\x01h\x00\x00\x00\xa4\x00\x00\x9b\xf3\xd5\x1f\xef\xb1\xcf\x97\x93\xb6=f\x8f~\xd6na\xf4j\x9c\xf6\xd9\x12-\x06yZ\xbb-Uk!\xe1XHd\x9b\xb9`\xba\xfcA\xcb\xddM&V<\xfcA\xfc\xfc\xe6A\x87\xef\xac\x96\x95c\xb4\xc6c\x0c\x8c\xdb\xaa\xa7\x7f\x89\xbd\x00_\xe3\x93>\xe5\xf4)(\xe4\xe3\x08Z\xa6\xce\xedW\x0c\x94(\xdc\xeb<\xa9\xa4]\x962\xbaX\x8c\x8b\x03\xbb\xccVtn\xcfZ\x8e\xd03\x97t\xe0\x99F\x8c\x89\xdf\x15=\x9b\xd8\x0cM'

    smplk3 = "\x01\x02\x00\x00\x01h\x00\x00\x00\xa4\x00\x00Q\xb1uo\xd8yn\x01\xd1\x1e\x88\xe3\xdaM\x00\xc2\xf6\x83i\xc39\x9a0\xbe\x1d\xff\xa4\xe5\xa5<zG\xd0'\xd2,\xca*,\xd0j!\xaa}\x17\xbd\x03\xdb\xf4\x96S\xbec\xaa\xb7\xd3\xc7\x06]\x19\xb0\x1a\xa4LJ\xe1\x81 ;\x1b\x11\x9e\xf7\xfb\x1fnV\xecO\x01\xee\xcb\xcc\x91\x95\x1d\x89\x14\xc6>\x80\xdf\x8e\xf2\x99A:n\x1f\xd3\x89\xa9tv\x0fw%\x14G\xf8\x11\x1dj_\x1f\xff\xaa\xc8\xea\xdb`Q\xe5W@\xa9i\xca"

    pubkey = '0602000000a40000525341310004000001000100a111c7c06d5a0bfe352714cc48fb1b11d33654bcc67ef698242c6a5ac5388b44fe8f66ac7c943770a9d6fb802fa6e5a3b3f94c26b3a447ad8ff144c6045e8a63f3beea2da9dc32db22a9ca4048e6095b1592816fa040c24695dc27d87f7b01a1e8a8595b9fb356ea836da73e02ecda2d8a082d567a8b744f18c8d7ceebf804a5'.decode(
        'hex')

    xkey = "A" * 0x10
    print len(smplk), len(smplk2), len(smplk3)

    c = import_key(smplk2, privkey=pkey)
    print c

    kk = export_key('rc4_enc', xkey, pubkey=key)
    print len(kk)
    print `kk`

    c = import_key(kk, privkey=key)
    print c
    print c.key

    print `export_key('rc4_enc', xkey)`
