
def rol(x, n, b=32):
    n = (b-1) & n
    return x << n | 2 ** n - 1 & x >> b - n


def chunks(data, n):
    return [data[i*n:(i+1)*n] for i in range(len(data)/n)]


def ror(n, bits,b=32):
    return rol(n, b - (b & bits),b)
