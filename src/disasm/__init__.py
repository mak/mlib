import capstone as _c
import capstone.x86 as cpu
from .hash import x86_hash_table


class Op(object):
    _regs = dict(map(lambda x: (x.split(
        '_')[-1].lower(), getattr(cpu, x)), filter(lambda x: x.startswith('X86_REG_'), dir(cpu))))
    _xregs = dict(map(lambda x: (getattr(cpu, x), x.split(
        '_')[-1].lower()), filter(lambda x: x.startswith('X86_REG_'), dir(cpu))))
    _xregs[0] = None
    _8bit_regs = [cpu.X86_REG_AH, cpu.X86_REG_AL, cpu.X86_REG_BH, cpu.X86_REG_BL,
                  cpu.X86_REG_CH, cpu.X86_REG_CL, cpu.X86_REG_DH, cpu.X86_REG_DL]

    def __init__(self, op):
        self.op = op

    @property
    def type(self):
        return self.op.type

    @property
    def is_imm(self):
        return self.type == cpu.X86_OP_IMM

    @property
    def is_reg(self):
        return self.type == cpu.X86_OP_REG

    @property
    def is_mem(self):
        return self.type == cpu.X86_OP_MEM

    @property
    def val(self):
        if self.is_imm:
            return self.op.value.imm
        elif self.is_reg:
            return self._xregs[self.op.value.reg]
        elif self.is_mem:
            return self.op.value.mem.disp

    @property
    def reg(self):
        if self.is_reg:
            return self.val
        elif self.is_mem:
            x = self.op.value.mem.base
            return self._xregs[x or self.op.value.mem.index]
        return ''

    @property
    def is_8bit_reg(self):
        return self.is_reg and self.op.value.reg in self._8bit_regs

    def __eq__(self, op):
        r = False
        if self.is_mem and getattr(op, 'is_mem', False):
            r |= all(map(lambda a: getattr(self.op.mem, a) == getattr(op.op.mem, a),
                         ['base', 'disp', 'index', 'scale']))
        elif self.is_reg and (type(op) == str or getattr(op, 'is_reg', False)):
            r |= self.reg == (op if type(op) == str else op.reg)

        elif self.is_imm and (type(op) == int or getattr(op, 'is_imm', False)):
            r |= self.val == (op if type(op) == int else op.val)
        return r

# class that abstract away disassembly access
# base module is capston engine


TBL_0F = 256  # /* table index: 0F-prefixed opcodes        */
TBL_80_83 = 512  # /* table index: 80/81/82/83 /ttt           */
TBL_F6 = 520  # /* table index: F6 /ttt                    */
TBL_F7 = 528  # /* table index: F7 /ttt                    */
TBL_FE = 536  # /* table index: FE /ttt                    */
TBL_FF = 544  # /* table index: FF /ttt                    */


class C(object):

    _groups = dict(map(lambda x: (x.split(
        '_')[-1].lower(), getattr(cpu, x)), filter(lambda x: x.startswith('X86_GRP_'), dir(cpu))))

    def __init__(self, _ins, b):
        self.ins = _ins
        self.mnem = self.ins.mnemonic
        self.base = b
        self.operands = map(Op, self.ins.operands)
        self.size  = self.ins.size
        self.address = self.ins.address
        
    def __str__(self):
        return "%s %s" % (self.mnem, self.ins.op_str)

    def __repr__(self):
        return "0%x: %s" % (self.ins.address, self.__str__())

    @property
    def instr_hash(self):
        if not hasattr(self, '_instr_hash'):
            h = None
            if self.ins.opcode[0] == 0xf:
                h = x86_hash_table[TBL_0F + self.ins.opcode[1]]
            elif self.ins.modrm:
                modrm_reg = (self.ins.modrm & 0x38) >> 3
                if (self.ins.opcode[0] & 0xFC) == 0x80:
                    h = x86_hash_table[TBL_80_83 + modrm_reg]
                elif self.ins.opcode[0] == 0xF6:
                    h = x86_hash_table[TBL_F6 + modrm_reg]
                elif self.ins.opcode[0] == 0xF7:
                    h = x86_hash_table[TBL_F7 + modrm_reg]
                elif self.ins.opcode[0] == 0xFE:
                    h = x86_hash_table[TBL_FE + modrm_reg]
                elif self.ins.opcode[0] == 0xFF:
                    h = x86_hash_table[TBL_FF + modrm_reg]
            if not h:
                h = x86_hash_table[self.ins.opcode[0]]

            self._instr_hash = h

        return self._instr_hash

    @property
    def regs_access(self):
        # lets cache this, it looks
        if not hasattr(self, '_regs_acc'):
            self._regs_acc = map(self.ins.reg_name, self.ins.regs_access())
        return self._regs_acc

    @property
    def regs_write(self):
        return self.regs_access[1]

    @property
    def regs_read(self):
        return self.regs_access[0]

    def op(self, idx):
        return self.operands[idx]

    def group(self, grp):
        if type(grp) == str:
            grp = self._groups[grp]
        return self.ins.group(grp)

    def val(self, idx):
        return self.op(idx).val

    def reg(self, idx):
        return self.op(idx).reg

    def type(self, idx):
        return self.op(idx).type

    def is_imm(self, idx):
        return self.op(idx).is_imm

    def is_reg(self, idx):
        return self.op(idx).is_reg

    def is_mem(self, idx):
        return self.op(idx).is_mem


def disasm(base=None, data=None, address=None):
    md = _c.Cs(_c.CS_ARCH_X86, _c.CS_MODE_32)
    md.detail = True
    for i in md.disasm(data, address):
        yield C(i, base)

# compute SPP(small-prime-product) from diassembled code


def spp_hash(base=None, data=None, address=None, code=None):
    if code:
        return reduce(lambda x, y: x * y.instr_hash, code, 1)
    else:
        return spp_hash(code=disasm(base, data, address))
