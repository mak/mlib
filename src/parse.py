import mlib
from mlib.struct import udword
from mlib.winapi.crypto import import_key


def parse_pubkey_rsa(rsa_bin, ignore_len=False):
    r = import_key(rsa_bin, dump_key=True)
    if not r:
        return rsa_bin.encode('hex')
    r['n'] = str(r['n'])
    if 'd' in r:
        r['d'] = str(r['d'])
    return r


def parse_key_ecc(ecc_bin):
    s = udword(ecc_bin)
    ecc_bin = ecc_bin[4:4 + s]
    keys = udword(ecc_bin, off=4)
    t = {'ECS3': 'ecdsa_pub_p384', 'ECS4': 'ecdsa_priv_p384'}[ecc_bin[0:4]]
    x = ecc_bin[8:8 + keys]
    y = ecc_bin[8 + keys:keys * 2 + 8]
    return {'t': t, 'x': str(int(x.encode('hex'), 16)), 'y': str(int(y.encode('hex'), 16))}


def parse_asn1_pubkey(asn1):
    import bitarray
    from pyasn1.codec.der.decoder import decode
    bs = decode(asn1)[0][1]  # frist is some oid
    try:
        b = bitarray.bitarray(str(bs).replace(',', '').replace(' ', '')[1:-1])
        # backward compatibility?
        v = decode(b.tobytes())[0]
    except:
        b = bitarray.bitarray(str(bs))
        v = decode(b.tobytes())[0]

    return {'n': str(v[0]), 'e': int(str(v[1]))}


generic_parse = mlib.misc.generic_parse
