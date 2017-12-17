import sys
from abstract import PE
from Queue import Queue
from collections import namedtuple
from threading import current_thread, Lock, Thread, Event


BB = namedtuple('BB', ['begin', 'end', 'size',
                       'code', 'ins_count',
                       'frm', 'to'
                       ]
                )


def is_exit(impr):
    r = False
    if impr['dll'] == 'msvcrt.dll':
        r |= impr['name'] == '_exit'
        r |= impr['name'] == 'exit'
    if impr['dll'] == 'kernel32.dll':
        r |= impr['name'] == 'ExitProcess'
    return r


class E():

    def __init__(self, ldr):

        self._bb_lock = Lock()
        self._done = []
        self.ldr = ldr

        # basic blocks...
        self._bb = {}
        self._bb_range = {}

        self.funcs = []
        self.xrefs = {}
        self.switch_jmp = []

    def bb(self, a):
        if a in self._bb:
            return self._bb[a]
        if a in self._bb_range:
            return self._bb_range[a]

        for bb in self._bb.values():
            if bb.begin <= a < bb.end:
                self._bb_range[a] = bb
                return bb

#    def track_val_in_bb(self,op,bb):

    def add_xref(self, t, f):
        if f not in self.xrefs:
            self.xrefs[f] = []
        if t not in self.xrefs:
            self.xrefs[t] = []

        self.xrefs[f].append(t)
        self.xrefs[t].append(f)

    def do_address(self, f, a, x=None, func=False):
        # print '%x -> %x' % (x,a)
        if x:
            self.add_xref(x, a)
        if func:
            self.funcs.append(a)
        self.q.append((f, a))
#        self.disas_block(None,a)

    def can_be_function(self, a):
        r = False
        if self.ldr.is_exec(a):
            r = self.ldr.read(a, 3) == '\x55\x8b\xec'
        return r

    def analyze_call(self, c):
        if c.is_mem(0) and not c.reg(0):
            # just simple call via memory
            # could be library call or some other

            if c.val(0) not in self.ldr.imports:
                try:
                    addr = self.ldr.dword(c.val(0))
                except:
                    return

                if self.ldr.is_exec(addr):
                    self.do_address(None, addr, c.ins.address)
                    self.add_xref(c.val(0), c.ins.address)

            elif c.val(0) in self.ldr.imports \
                    and is_exit(self.ldr.imports[c.val(0)]):
                self.add_xref(c.val(0), c.ins.address)
                return -1
            elif c.val(0) in self.ldr.imports:
                self.add_xref(c.val(0), c.ins.address)

        elif c.is_imm(0) and not c.reg(0):
            self.do_address(None, c.val(0), c.ins.address)
            # self.add_xref(c.val(0),c.ins.address)
            # self.q.put(c.val(0))

    def _disas_block(self, addr):

        cc = []
        to = []
        ends_with_jump = False

        for c in self.ldr.disasm(addr, 0x100):
            cc.append(c)
#            print repr(c),map(c.ins.group_name,c.ins.groups),c.ins.group(1)
            if c.group('ret'):
                if len(cc) >= 2 and cc[-2].mnem == 'push':
                    print '%x hack!' % c.ins.address
                break

            elif c.group('jump'):
                if c.is_imm(0):
                    self.do_address(addr, c.val(0), c.ins.address)
                    to.append(c.val(0))

                elif c.mnem == 'jmp' and c.is_mem(0) and c.reg(0):
                    # this can be switch jump
                    self.switch_jmp.append(addr)

                elif c.mnem == 'jmp' and c.reg(0):
                    # indirect jump, propably switch
                    self.switch_jmp.append(addr)

                ends_with_jump = c.mnem != 'jmp'
                break
            elif c.group('call'):
                if self.analyze_call(c) == -1:
                    break

            elif c.mnem == 'push' and c.is_imm(0) and self.can_be_function(c.val(0)):
                self.do_address(None, c.val(0), c.ins.address)

            elif c.mnem == 'mov' and c.is_imm(1) and self.can_be_function(c.val(1)):
                self.do_address(None, c.val(1), c.ins.address)

        if len(cc) == 1 and cc[0].mnem == 'jmp':
            # TODO:this usless indirection that should be delt with
            if c.val(0) in self.ldr.imports:
                for a in self.xrefs[addr]:
                    self.add_xref(a, c.val(0))

        end = c.ins.address + c.ins.size
        if ends_with_jump:
            self.do_address(addr, end, None)
 #           self.q.put((addr,end))
            to.append(end)

        return BB._make([addr, end, end - addr, cc, len(cc), [], to])

    def solve_switch_jump(self, a):
        print hex(a)

        # lets fire some heuristics,
        # we travel max 5 blocks back
        bb = self.bb(a)
        ins = bb.code[-1]
        op = ins.reg(0)
        cnt = 0
        addr = None
        jmps = []
        for i in range(5):
            prev_ins = None
            for c in reversed(bb.code):
                print `c`, '|', op
                if c.mnem == 'cmp':
                    if c.op(0) == op:
                        cnt = c.val(1)
                        break
                    elif c.op(1) == op:
                        cnt = c.val(0)
                        break
                #    else:

                elif c.mnem in ['lea', 'mov'] and c.op(0) == op:
                    if not c.is_mem(1) or not c.reg(1):
                        op = c.op(1)
                    elif not c.disp(1):
                        op = c.reg(1)
                        print 'hmm'
                    elif c.reg(1) == 'esp':
                        op = c.op(1)

                elif c.mnem == 'add' and c.op(0) == op:  # ,'sub','shl','shr']:
                    if c.is_imm(1):
                        # this is propably our address
                        addr = c.val(1)

                prev_ins = c
            if cnt:
                break
            bb = self.bb(bb.frm[0])

        if not addr:
            addr = ins.val(0)
        if cnt:
            print addr, cnt
            jmps = [self.ldr.dword(addr + 4 * i)for i in range(cnt + 1)]
        return jmps

    def run_in_loop(self):
        _done = []
        while self.q:

            from_addr, addr_to = self.q.pop()
            if not addr_to in _done:
                _done.append(addr_to)
                bb = self._disas_block(addr_to)
                self._bb[addr_to] = bb

            if from_addr:
                self._bb[addr_to].frm.append(from_addr)

    def run(self):

        self.q = []
        self.do_address(None, self.ldr.entry, None)
        self.run_in_loop()
        print '[*] dicoverd bb: %d' % len(self._bb)
        # print '[*] problems with %d switch-case' % len(self.switch_jmp)
        print map(hex, self.switch_jmp)
        # for a in self.switch_jmp:
        #
#            _pool.apply_async(self.disas_block,(addr,))


with open(sys.argv[1]) as f:
    d = f.read()
p = PE(_data=d)
engine = E(p)
print hex(p.entry)
engine.run()
print engine.bb(0x040158C)
print engine.bb(0x04015BD)
print engine.bb(0x040157D)
for a in engine.switch_jmp:
    bb = engine.bb(a)
    last_addr = bb.code[-1].ins.address
    for a0 in engine.solve_switch_jump(a):
        bb.to.append(a0)
        engine.do_address(a, a0, last_addr)
engine.run_in_loop()
xbb = engine.bb(0x0402814)
print xbb.code[0].group('jump')
print engine.xrefs[0x401584]

print hex(p.imports['printf']['addr'])
print engine.xrefs[p.imports['printf']['addr']]


# print hex(timesmth)


# ins2=engine.bb(0x0407C77).code[-1]
# print ins2
# print ins2.ins.regs_access()

# print len(engine.bb)
# print 0x403412 in engine.bb

# import json
# ida_bb = json.load(open('/tmp/bb'))
# # for bb in engine.bb:
# #     if bb not in ida_bb:
# #         print 'huh ida didnt found it?...',hex(bb)
# for bb in ida_bb:
#     if bb not in engine.bb:
#         print 'huh i didnt found it?...',hex(bb)
