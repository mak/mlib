from . import C
import capstone as cs

class DummyIns(object):

    def group(self,grp):
        return ''


class DummyOp(object):
    pass

class DummyVal(object):
    pass


def mk_inst(addr,base,mnem,bytes,ops=[],op_str=''):
    i  = DummyIns()
    i.mnemonic = mnem
    i.address  = addr
    i.opcode   = bytes 
    i.operands = ops
    i.op_str   = op_str
    i.size     = len(bytes)
    return C(i,base)

vm_table = [
    ['vmgetinfo','vmsetinfo','vmdxdsbl','vmdxenbl'],
    ['vmcpuid', 'vmhlt','vmsplaf'],
    ['vmpushfd','vmpopfd','vmcli','vmsti','vmiretd'],
    ['vmsgdt','vmsidt','vmsldt','vmstr'],
    ['vmsdte'],
]
def decode_vm(ldr,addr):

    b0 = ldr.byte(addr)
    if b0 not in (0x0f,0xf0,0x66):
        # one of intels prefixes
        return None

    b1 = ldr.byte(addr+1)
    if b1 == 0x3f:
        b2 = ldr.byte(addr+2)
        b3 = ldr.byte(addr+3)
        if b2 in (0x01,0x05,0x07,0x0d,0x10) and b3:

            op1 = DummyOp()
            op1.type = cs.CS_OP_IMM
            op1.value = DummyVal()
            op1.value.imm = b2

            op2 = DummyOp()
            op2.type = cs.CS_OP_IMM
            op2.value = DummyVal()
            op2.value.imm = b3

            op_str = '%xh, %xh' % (b2,b3)
            ops =[op1,op2]
            b = [b0,b1,b2,b3]
            i  = mk_inst(addr,ldr.base,'vpcext',b,ops,op_str)
            return i
        
    elif b1 in (0xc6,0xc7):
        b2 = ldr.byte(addr+2)
        if b2 in (0x28,0xc8):
            b3 = ldr.byte(addr+3)
            b4 = ldr.byte(addr+4)
            b = [b0,b1,b2,b3,b4]

            if b3 < len(vm_table) and b4 < len(vm_table[b3]):
                i = mk_inst(addr,ldr.base,vm_table[b3][b4],b)
                return i

    elif b1 == 0x01:
        b2 = ldr.byte(addr+2)
        idx = b2 - 0xc0
        tbl = [ "vmxoff","vmcall","vmlaunch","vmresume","vmxon"]
        if idx < 5:
            i = mk_inst(addr,ldr.base,tbl[idx],[b0,b1,b2])
            return i
    return None
