
MASK_16 = 2 ** 16 - 1
MASK_32 = 2 ** 32 - 1
MASK_64 = 2 ** 64 - 1


def uint(n, bits):
    mask = globals().get('MASK_%d' % bits, None)
    if not mask:
        mask = 2 ** bits - 1
    return n & mask


def uint32(num):
    return uint(num, 32)


def bswap32(n):
    return (((n & 0x000000FF) << 24) |
            ((n & 0x0000FF00) << 8) |
            ((n & 0x00FF0000) >> 8) |
            ((n & 0xFF000000) >> 24))


def bswap16(n):
    return (((n & 0x000000FF) << 8) |
            ((n & 0x0000FF00) >> 8))


def bswap64(n):
    return (((n & 0x00000000000000FF) << 56) |
            ((n & 0x000000000000FF00) << 40) |
            ((n & 0x0000000000FF0000) << 24) |
            ((n & 0x00000000FF000000) << 8) |
            ((n & 0x000000FF00000000) >> 8) |
            ((n & 0x0000FF0000000000) >> 24) |
            ((n & 0x00FF000000000000) >> 40) |
            ((n & 0xFF00000000000000) >> 56))


def bswap(n, bits):
    if bits not in (16, 32, 64):
        raise Exception("i can't swap those bits")
    return globals().get('bswap%d' % bits)(n)


def rol(x, n, b=32):
    n = (b - 1) & n
    return x << n | 2 ** n - 1 & x >> b - n


def chunks(data, n):
    return [data[i * n:(i + 1) * n] for i in range(len(data) / n)]


def ror(n, bits, b=32):
    return rol(n, b - bits, b)
