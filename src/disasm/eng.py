import re
import sys
from Queue import Queue
from collections import namedtuple
from threading import current_thread, Lock, Thread, Event

from . import vmext

BB = namedtuple('BB', ['begin', 'end', 'size',
                       'code', 'ins_count',
                       'frm', 'to',
                       'funcs'
                       ]
                )
F = namedtuple('F', ['bbs','addr'])
    
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

        # functions
        self._funcs = set()
        self._funcs_obj = {}
        self._funcs_range = []

        self.xrefs = {}
        self.drefs = {}
        
        self.switch_jmp = []

        self._from_changes = {}
        
    def disasm_one(self,addr):
        try:
            i = self.ldr.disasm(addr, 15).next()
            return i
        except StopIteration:
            pass

        b = self.ldr.byte(addr)
        if b in (0x3e,0x2e):
            # just swallow branch predicitions
            waddr = addr+1
            while b in (0x3e,0x2e):
                b = self.ldr.byte(waddr)
                waddr += 1
            
            i = self.disasm_one(waddr-1)
            i.address = addr
            i.size += waddr-addr-1
            return i
        
        i = vmext.decode_vm(self.ldr,addr)
        if not i:
            raise Exception("Can't decode instruction at 0x%x"%addr)
        return i
        
    @property
    def funcs(self):
        return list(self._funcs)

    def function(self, addr):
        if addr in self._funcs_obj:
            return self._funcs_obj[addr]
        
        if addr not in self._funcs:
            ## this is kinda bad since bb can be part of many functions
            try:
                addr = iter(self.bb(addr).funcs).next()
            except StopIteration:
                self._funcs_obj[addr] = None
                return None
        
        bbs = self.get_reachable_blocks(addr)
        func = F._make([bbs,addr])
        self._funcs_obj[addr] = func
        return func

    def bb(self, a, dont_cache=False):
        if a in self._bb:
            return self._bb[a]
        if a in self._bb_range:
            return self._bb_range[a]

        for bb in self._bb.values():
            if bb.begin <= a < bb.end:
                if not dont_cache:
                    self._bb_range[a] = bb
                return bb

    def get_reachable_blocks(self,addr):
        q = [addr]
        r = set()
        while q:
            a = q.pop()
            if a not in r:
                r.add(a)
                for a in self.bb(a).to:
                    q.append(a)
        return map(lambda a: self.bb(a),r)
            #    def track_val_in_bb(self,op,bb):
            
    def _add_ref(self, t, f, store):
        if f not in store:
            store[f] = []
        if t not in store:
            store[t] = []

        store[f].append(t)
        store[t].append(f)

    def add_xref(self, t, f):
        return self._add_ref(t, f, self.xrefs)

    def add_dref(self, t, f):
        return self._add_ref(t, f, self.drefs)

    def do_address(self, f, a, lf, x=None, func=False):
        #print '%x -> %x' % (x or -1,a)
        if x:
            self.add_xref(x, a)
        if func:
            self._funcs.add(a)
        
        self.q.append((f, a, a if func else lf ))
#        self.disas_block(None,a)

    def can_be_function(self, a):
        r = False
        if self.ldr.is_exec(a):
            r =  self.ldr.read(a, 3) == '\x55\x8b\xec'
            r |= self.ldr.read(a, 2) == "\xff\x25" and\
                 self.ldr.is_addr(self.ldr.dword(a+2))
            if r:
                return r
            
            try:
                ## can be setting up a SEH handler...
                i0 = self.disasm_one(a)
                i1 = self.disasm_one(a + i0.size)
                i2 = self.disasm_one(a + i1.size + i0.size)
                mnems = map(lambda i: i.mnem,[i0,i1,i2])
                r  = mnems == ['push','push','call']
                r &= i0.is_imm(0) and i0.val(0) < 0x4000
                r &= i1.is_imm(0) and self.ldr.is_addr(i1.val(0))
            except:
                pass
            
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
                    self.do_address(None, addr, -1, c.address, func=True)
                    self.add_xref(c.val(0), c.address)

            elif c.val(0) in self.ldr.imports \
                    and is_exit(self.ldr.imports[c.val(0)]):
                self.add_xref(c.val(0), c.address)
                return -1
            elif c.val(0) in self.ldr.imports:
                self.add_xref(c.val(0), c.address)

        elif c.is_imm(0) and not c.reg(0):
            self.do_address(None, c.val(0), -1, c.address, func=True)
            # self.add_xref(c.val(0),c.address)
            # self.q.put(c.val(0))
    def analyze_dref(self,c):
        dst = None
        for op in c.operands:
            if op.is_imm and self.ldr.is_data(op.val):
                dst = op.val
                break
            if op.is_mem and self.ldr.is_data(op.val):
                dst = op.val
                break
        if dst is not None:
            self.add_dref(dst,c.address)
        
    def _disas_block(self, addr, lf):

        cc = []
        to = []
        ends_with_ccjump = False
        waddr = addr
        
        while True:
            
            c = self.disasm_one(waddr)
            cc.append(c)
            
            self.analyze_dref(c)
            if c.group('ret'):
                if len(cc) >= 2 and cc[-2].mnem == 'push':
                    print '%x hack!' % c.address
                break

            elif c.group('jump'):
                if c.is_imm(0):
                    self.do_address(addr, c.val(0), lf, c.address)
                    to.append(c.val(0))

                elif c.mnem == 'jmp' and c.is_mem(0) and c.reg(0):
                    # this can be switch jump
                    self.switch_jmp.append(addr)

                elif c.mnem == 'jmp' and c.reg(0):
                    # indirect jump, propably switch
                    self.switch_jmp.append(addr)

                ends_with_ccjump = c.mnem != 'jmp'
                break
            
            elif c.group('call'):
                if self.analyze_call(c) == -1:
                    break

            elif c.mnem == 'push' and c.is_imm(0) and self.can_be_function(c.val(0)):
                self.do_address(None, c.val(0), -1, c.address, func=True)

            elif c.mnem == 'mov' and c.is_imm(1) and self.can_be_function(c.val(1)):
                self.do_address(None, c.val(1), -1, c.address, func=True)

            waddr += c.size
            if waddr in self._done:
                #print 'donelbock',hex(addr),hex(waddr)
                to.append(waddr)
                break
                
        if len(cc) == 1 and cc[0].mnem == 'jmp':
            # TODO:this usless indirection that should be delt with
            if c.val(0) in self.ldr.imports:
                for a in self.xrefs[addr]:
                    self.add_xref(a, c.val(0))

        end = c.address + c.size
        if ends_with_ccjump:
            #print 'ccj',hex(waddr),hex(end),hex(lf)
            self.do_address(addr, end, lf)
            to.append(end)

        return BB._make([addr, end, end - addr, cc, len(cc), [], to,set() ])

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
                    elif c.is_mem(1) and not c.val(1):
                        op = c.reg(1)
                        print 'hmm'
                    elif c.is_mem(1) and c.val(1):
                        pass
                        
                    elif c.reg(1) in ('esp','ebp'):
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
            # print addr, cnt
            jmps = [self.ldr.dword(addr + 4 * i)for i in range(cnt + 1)]
        return jmps

    def _split_bb(self,bb,new_begin):
        # print 'spliting bb'
        # print hex(int(bb.begin)),bb
        # print hex(int(new_begin))

        if new_begin <= bb.begin:
            return bb

        for idx,c in enumerate(bb.code):
            if c.address == new_begin:
                break

        # print hex(idx)
        new_size = new_begin - bb.begin
        new_bb = BB._make([bb.begin,new_begin, new_size, bb.code[:idx],
                           idx,bb.frm,[new_begin],bb.funcs])
        self._bb[bb.begin] = new_bb        
        new_bb = BB._make([new_begin,bb.end,bb.size - new_size,
                           bb.code[idx:],bb.ins_count - idx,[],bb.to,
                           bb.funcs])
        
        new_bb.frm.append(bb.begin)

        ## update references in other bb's
        for baddr in bb.to:
            b = self.bb(baddr,dont_cache=True)
            if b:
                if bb.begin in b.frm:
                    b.frm.remove(bb.begin)
                    b.frm.append(new_begin)
                else:
                    ## this block was anlyzed but reference is still
                    ## in queue, make changing of from address
                    self._from_changes[(bb.begin,baddr)] = new_begin    
            else:
                ## this bblock is in queue, lets mark that
                ## from address must be changed
                self._from_changes[(bb.begin,baddr)] = new_begin
        
        del bb
        return new_bb


    
    # def _clean_bbs(self):
    #     for bb_a in self._bb:
    #         ns = 0
    #         bb = self._bb[bb_a]
    #         for i,c in enumerate(bb.code):
    #             other_bb = self.bb(c.address,dont_cache=True)
    #             if bb_a != other_bb.begin:
    #                 self._split_bb(bb,other_bb,ns,i)
    #                 break
    #             ns += c.size

    
    def _run_in_loop(self):
        self._done = []
        newf = False
        while self.q:
            newf = True
            from_addr, addr_to, lf = self.q.pop()
            if not addr_to in self._done:
                bb0 = self.bb(addr_to,dont_cache=True)
                if bb0:
                    #print 'bb already exits',hex(addr_to)
                    bb = self._split_bb(bb0,addr_to)
                else:
                    self._done.append(addr_to)
                    bb = self._disas_block(addr_to,lf)
                    
                self._bb[addr_to] = bb
                
            self._bb[addr_to].funcs.add(lf)
            if from_addr:
                from_addr = self._from_changes.get((from_addr,addr_to),from_addr)
                #print 'frm',hex(addr_to),hex(from_addr)
                self._bb[addr_to].frm.append(from_addr)
        return newf
    
    def add_seh_records_v3(self):
        exp_hdlr = self.ldr.imports.get('_except_handler3')       
        if not exp_hdlr or exp_hdlr['dll'] != 'msvcrt.dll':
            return
        
        exp_hdlr = exp_hdlr['addr']
        sehp = self.xrefs[exp_hdlr][0]
        # TODO verify if this is __SEH_prolog indeed
        for xr in self.xrefs[sehp]:
            #print '----'
            b = self.bb(xr)
            if not b: continue
    
            for i,ins in enumerate(b.code):
                if ins.address == xr:
                    break
            if ins.mnem != 'call':
                continue

            seh_rec = b.code[i-1].val(0)
            stack_size = b.code[i-2].val(0)
            # print hex(int(xr)),hex(seh_rec),stack_size
            # print `ins`
            try_start = []
            for b in self.get_reachable_blocks(xr):
                ## we need to find out how many times
                ## registration records are setted up
                for c in b.code:
                    if c.mnem in ('mov','and') and\
                       c.reg(0) == 'ebp' and c.is_mem(0) and\
                       c.val(0) == -4:
                        # print `c`
                        try_start.append(c.address)
                        
            for a in sorted(try_start):
                bb_a = self.bb(a)

                ## maintain ida compability
                bb_a = self._split_bb(bb_a,a)
                self._bb[a] = bb_a
                
                b_filter  = self.ldr.dword(seh_rec+4)
                b_handler = self.ldr.dword(seh_rec+8)
                if self.ldr.is_addr(b_filter) and\
                   self.ldr.is_exec(b_filter):

                    b = self.bb(b_filter)
                    if not b:
                        bb_a.to.append(b_filter)
                        for f in bb_a.funcs:
                            yield bb_a.code[-1].address,b_filter,f
                    else:
                        print 'dupa',hex(a),hex(b_filter)

                        
                if b_filter == b_handler:
                    continue
                    
                if self.ldr.is_addr(b_handler) and\
                   self.ldr.is_exec(b_handler):

                    b = self.bb(b_handler)
                    if not b:
                        bb_a.to.append(b_handler)
                        for f in bb_a.funcs:
                            yield bb_a.code[-1].address,b_handler,f
                    else:
                        print 'dupa',hex(a),hex(b_filter)
                seh_rec += 0x0c
                
    def run(self):

        self.q = []
        self.do_address(None, self.ldr.entry, -1, None, func=True)
        self._run_in_loop()

        idx = 0
        while True:
            print 'add seh3 round %d' % idx
            newblocks = self.add_seh_records_v3()
            for frm,addr,f in newblocks:
                print 'newblock',hex(frm),hex(addr)
                self.do_address(frm,addr,f)


            if not self._run_in_loop():
                break
            idx +=1
        #self._run_in_loop()

        
        # print '[*] dicoverd bb: %d' % len(self._bb)
        # print '[*] problems with %d switch-case' % len(self.switch_jmp)
        # print map(hex, self.switch_jmp)
        # for a in self.switch_jmp:
        #
#            _pool.apply_async(self.disas_block,(addr,))


# with open(sys.argv[1]) as f:
#     d = f.read()
# p = PE(_data=d)
# engine = E(p)
# print hex(p.entry)
# engine.run()
# print engine.bb(0x040158C)
# print engine.bb(0x04015BD)
# print engine.bb(0x040157D)
# for a in engine.switch_jmp:
#     bb = engine.bb(a)
#     last_addr = bb.code[-1].address
#     for a0 in engine.solve_switch_jump(a):
#         bb.to.append(a0)
#         engine.do_address(a, a0, last_addr)
# engine.run_in_loop()
# xbb = engine.bb(0x0402814)
# print xbb.code[0].group('jump')
# print engine.xrefs[0x401584]

# print hex(p.imports['printf']['addr'])
# print engine.xrefs[p.imports['printf']['addr']]
