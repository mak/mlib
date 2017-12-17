class Spritz:

    def __init__(self, op):
        self.initialise_state()
        self.op = op

    def encrypt(self, K, M):
        self.initialise_state()
        self.absorb(K)
        return bytearray(self.op(b1, b2) for b1, b2 in zip(M, self.squeeze(len(M))))

    def decrypt(self, K, C):
        self.initialise_state()
        self.absorb(K)
        return bytearray(self.op(b1, b2) for b1, b2 in zip(C, self.squeeze(len(C))))

    def hash(self, M, r):
        self.initialise_state()
        self.absorb(M)
        self.absorb_stop()
        self.absorb(bytearray(self.base_10_to_256(r)))
        return self.squeeze(r)

    def swap(self, i1, i2):
        self.S[i1], self.S[i2] = self.S[i2], self.S[i1]

    def initialise_state(self):
        self.i = self.j = self.k = self.z = self.a = 0
        self.w = 1
        self.S = bytearray(range(256))

    def absorb(self, I):
        for b in I:
            self.absorb_byte(b)

    def absorb_byte(self, b):
        self.absorb_nibble(b & 0xf)
        self.absorb_nibble(b >> 4)

    def absorb_nibble(self, x):
        if self.a == 128:
            self.shuffle()
        self.swap(self.a, 128 + x)
        self.a = self.add(self.a, 1)

    def absorb_stop(self):
        if self.a == 128:
            self.shuffle()
        self.a = self.add(self.a, 1)

    def shuffle(self):
        self.whip(512)
        self.crush()
        self.whip(512)
        self.crush()
        self.whip(512)
        self.a = 0

    def whip(self, r):
        for _ in range(r):
            self.update()
        self.w = self.add(self.w, 2)

    def crush(self):
        for v in range(128):
            if self.S[v] > self.S[255 - v]:
                self.swap(v, 255 - v)

    def squeeze(self, r):
        if self.a > 0:
            self.shuffle()
        return bytearray([self.drip() for _ in range(r)])

    def drip(self):
        if self.a > 0:
            self.shuffle()
        self.update()
        return self.output()

    def update(self):
        self.i = self.add(self.i, self.w)
        self.j = self.add(self.k, self.S[self.add(self.j, self.S[self.i])])
        self.k = self.add(self.i, self.k, self.S[self.j])
        self.swap(self.i, self.j)

    def output(self):
        self.z = self.S[self.add(self.j, self.S[self.add(
            self.i, self.S[self.add(self.z, self.k)])])]
        return self.z

    def add(self, *args):
        return sum(args) % 256

    # def xor(self, a,b):
    #     return a ^ b

    def base_10_to_256(self, n):
        m = bytearray()
        while n:
            m.append(n % 256)
            n = n // 256
        return reversed(m)
