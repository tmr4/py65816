from py65.utils.conversions import itoa
from py65.utils.devices import make_instruction_decorator

# 65c816
#   Registers
#       a: represents both 8 and 16 bit accumulator (the 65816 C register is not modeled separately)
#       b: only valid in 8 bit mode (otherwise use high byte of a)
#
class MPU:
    # vectors
    RESET = 0xfffc
    COP = [0xffe4, 0xfff4]
    BRK = 0xffe6
    ABORT = [0xffe8, 0xfff8]
    NMI = [0xffea, 0xfffa]
    IRQ = [0xffee, 0xfffe]

    # processor flags
    NEGATIVE = 128
    OVERFLOW = 64
    MS = 32 # native mode
    UNUSED = 32 # emulation mode
    IRS = 16 # native mode
    BREAK = 16 # emulation mode
    DECIMAL = 8
    INTERRUPT = 4
    ZERO = 2
    CARRY = 1

    BYTE_WIDTH = 8
    BYTE_FORMAT = "%02x"
    WORD_WIDTH = 16
    WORD_FORMAT = "%04x"
    ADDR_WIDTH = 16
    ADDR_FORMAT = "%04x"
    ADDRL_WIDTH = 24
    ADDRL_FORMAT = "%05x"

    def __init__(self, memory=None, pc=0x0000):
        # config
        self.name = '65C816'
        self.waiting = False
        self.byteMask = ((1 << self.BYTE_WIDTH) - 1)
        self.addrMask = ((1 << self.ADDR_WIDTH) - 1)
        self.addrMaskL = ((1 << self.ADDRL_WIDTH) - 1) # *** TODO: do we need to restrict this more hardwired memory model limit? ***
        self.addrHighMask = (self.byteMask << self.BYTE_WIDTH)
        self.addrBankMask = (self.addrHighMask << self.BYTE_WIDTH) # *** TODO: should this be limited to 0x110000? ***

        # vm status
        self.excycles = 0
        self.addcycles = False
        self.processorCycles = 0

        if memory is None:
            memory = 0x10000 * [0x00]
        self.memory = memory
        #self.start_pc = 0xfffc
        self.start_pc = pc
        self.sp = 0

        # init
        self.reset()

# *** TODO: ***
    def reprformat(self):
        if self.mode:
            return ("%s PC   AC XR YR SP NV-BDIZC\n"
                    "%s: %04x %02x %02x %02x %02x %s")
        else:
            return ("%s B  K  PC   AC   XR   YR   SP   D    NVMXDIZC\n"
                    "%s: %02x %02x:%04x %04x %04x %04x %04x %04x %s")

# *** TODO: ***
    def __repr__(self):
        flags = itoa(self.p, 2).rjust(self.BYTE_WIDTH, '0')
        indent = ' ' * (len(self.name) + 1)
        if self.mode:
            return self.reprformat() % (indent, self.name, self.pc, self.a,
                                        self.x, self.y, self.sp, flags)
        else:
            return self.reprformat() % (indent, self.name, self.dbr, self.pbr, self.pc,
                                        self.a, self.x, self.y, self.sp, self.dpr, flags)

    def step(self):
        if self.waiting:
            self.processorCycles += 1
        else:
            instructCode = self.memory[self.pc]
            self.incPC()
            self.excycles = 0
            self.addcycles = self.extracycles[instructCode]
            self.instruct[instructCode](self)
            self.pc &= self.addrMask
            self.processorCycles += self.cycletime[instructCode] + self.excycles
        return self

    def reset(self):
        # pc is just the 16 bit program counter and must be combined with pbr to
        # access the program in memory
        self.pc = self.WordAt(self.RESET)

        # a, x and y are full 16 bit registers
        # they must be processed properly when in emulation mode
        self.a = 0
        self.b = 0 # b is 8 bit and hidden, it is only relevent in 8 bit
        self.x = 0
        self.y = 0

        self.p = self.BREAK | self.UNUSED
#        self.p = self.BREAK | self.UNUSED | self.INTERRUPT
        self.processorCycles = 0

        self.mode = 1
        self.dbr = 0
        self.pbr = 0
        self.dpr = 0

    def irq(self):
        # triggers a normal IRQ
        # this is very similar to the BRK instruction
        if self.p & self.INTERRUPT:
            return

        if self.mode:
            self.p &= ~self.BREAK
            self.p | self.UNUSED
        else:
            self.stPush(self.pbr)

        self.stPushWord(self.pc)
        self.stPush(self.p)

        self.p |= self.INTERRUPT
        self.pbr = 0
        self.pc = self.WordAt(self.IRQ[self.mode])
        self.processorCycles += 7

    def nmi(self):
        # triggers a NMI IRQ in the processor
        # this is very similar to the BRK instruction
        if self.mode:
            self.p &= ~self.BREAK
            self.p | self.UNUSED
        else:
            self.stPush(self.pbr)

        self.stPushWord(self.pc)
        self.stPush(self.p)

        self.p |= self.INTERRUPT
        self.pbr = 0
        self.pc = self.WordAt(self.NMI[self.mode])
        self.processorCycles += 7

    # Helpers for addressing modes and instructions

    def ByteAt(self, addr):
        return self.memory[addr]

    def WordAt(self, addr):
        return self.ByteAt(addr) + (self.ByteAt(addr + 1) << self.BYTE_WIDTH)

    # *** useful for debuging for now, may be able to incorporate them ***
    def LongAt(self, addr):
        return (self.ByteAt(addr + 2) << self.ADDR_WIDTH) + (self.ByteAt(addr + 1) << self.BYTE_WIDTH) + self.ByteAt(addr)

    def TCAt(self, addr):
        return (self.WordAt(addr + 2) << self.ADDR_WIDTH) + self.WordAt(addr)

    def WrapAt(self, addr):
        wrap = lambda x: (x & self.addrHighMask) + ((x + 1) & self.byteMask)
        return self.ByteAt(addr) + (self.ByteAt(wrap(addr)) << self.BYTE_WIDTH)

    def OperandAddr(self):
        return (self.pbr << self.ADDR_WIDTH) + self.pc

    def OperandByte(self):
        return self.ByteAt(self.OperandAddr())

    # *** TODO: likely these next two need some form of WrapAt
    def OperandWord(self):
        return self.WordAt(self.OperandAddr())

    def OperandLong(self):
        epc = self.OperandAddr()
        return (self.ByteAt(epc+2) << self.ADDR_WIDTH) + self.WordAt(epc)

    def incPC(self, inc=1):
        # pc must remain within current program bank
        self.pc = (self.pc + inc) & self.addrMask

    def bCLR(self, x):
        if self.p & x:
            self.incPC()
        else:
            self.ProgramCounterRelAddr()

    def bSET(self, x):
        if self.p & x:
            self.ProgramCounterRelAddr()
        else:
            self.incPC()

    def pCLR(self, x):
        self.p &= ~x

    def pSET(self, x):
        self.p |= x

    def isSET(self, x):
        return self.p & x # it's shorter just to inline this
        
    def isCLR(self, x):
        return not (self.p & x) # but not this
        
    # stack related helpers

    def stPush(self, z):
        if self.mode:
            self.memory[0x100 + self.sp] = z & self.byteMask
        else:
            self.memory[self.sp] = z & self.byteMask
        self.sp -= 1
        if self.mode:
            self.sp &= self.byteMask
        else:
            self.sp &= self.addrMask

    def stPop(self):
        self.sp += 1
        if self.mode:
            self.sp &= self.byteMask
        else:
            self.sp &= self.addrMask
        if self.mode:
            return self.ByteAt(0x100 + self.sp)
        else:
            return self.ByteAt(self.sp)

    def stPushWord(self, z):
        self.stPush((z >> self.BYTE_WIDTH) & self.byteMask)
        self.stPush(z & self.byteMask)

    def stPopWord(self):
        z = self.stPop()
        z += self.stPop() << self.BYTE_WIDTH
        return z

    def FlagsNZ(self, value):
        self.p &= ~(self.ZERO | self.NEGATIVE)
        if value == 0:
            self.p |= self.ZERO
        else:
            self.p |= value & self.NEGATIVE

    def FlagsNZWord(self, value):
        self.p &= ~(self.ZERO | self.NEGATIVE)
        if value == 0:
            self.p |= self.ZERO
        else:
            self.p |= (value >> self.BYTE_WIDTH) & self.NEGATIVE

    # Addressing modes

    # address modes have to return an effective address, which is something like:
    #   (self.dbr << self.ADDR_WIDTH) + self.pc
    # as they are invariably used to directly access memory or in functions that do
    # such as ByteAt and WordAt which take a simple offset into memory
    # Modes that use pbr (e.g. JMP, JSR, etc.) are handled separately in the instructions themselves
    # *** TODO: do we need to restrict effective address to memory model limit? ***

    # New 65816 Specific Addressing Modes:
    # -------------------------------------
    #    New Mode Name                             Example
    #    -------------------------------------------------------
    #    Absolute Long                             LDA $123456
    #    Absolute Long Indexed X                   LDA $123456,X
    #    Absolute Indexed Indirect                 JMP ($1234,X)
    #    Absolute Indirect Long                    JMP [$1234]
    #    Block Move                                MVP 0,0
    #    Direct Page Indirect                      LDA ($12)
    #    Direct Page Indirect Long                 LDA [$12]
    #    Direct Page Indirect Long Indexed Y       LDA [$77],Y
    #    Program Counter Relative Long             BRL $1234
    #    Stack Relative                            LDA 15,S
    #    Stack Relative Indirect Indexed Y         LDA (9,S),Y

    def AbsoluteAddr(self): # "abs" (26 opcodes)
        return (self.dbr << self.ADDR_WIDTH) + self.OperandWord()

    def AbsoluteXAddr(self): # "abx" (17 opcodes)
        tmp = self.OperandWord()
        a1 = (self.dbr << self.ADDR_WIDTH) + tmp
        a2 = a1 + self.x
        if self.addcycles:
            if (a1 & self.addrBankMask) != (a2 & self.addrBankMask):
                self.excycles += 1
        return a2

    def AbsoluteYAddr(self): # "aby" (9 opcodes)
        addr = self.OperandWord()
        a1 = (self.dbr << self.ADDR_WIDTH) + addr
        a2 = a1 + self.y
        if self.addcycles:
            if (a1 & self.addrBankMask) != (a2 & self.addrBankMask):
                self.excycles += 1
        return a2

    def AbsoluteIndirectAddr(self): # "abi" (1 opcodes)
        return (self.OperandWord() + (self.pbr << self.ADDR_WIDTH))

    def AbsoluteIndirectXAddr(self): # "aix" (2 opcodes)
        return (self.OperandWord() + self.x + (self.pbr << self.ADDR_WIDTH)) # & self.addrMask

    # Absolute Indirect Long "ail" (1 opcode) modeled directly in JMP as it has to change pbr

    def AbsoluteLongAddr(self): # new to 65816, "abl" (10 opcodes)
        # JML and JSL handle this mode separately as they has to change pbr
        return self.OperandLong()

    def AbsoluteLongXAddr(self): # new to 65816, "alx" (8 opcodes)
        # *** TODO: add 1 cycle if mode = 0 (do it either here or in instruction) generally it 
        # seems that it's done in address mode def ***
        return self.OperandLong() + self.x

    # Accumulator "acc" (6 opcodes) modeled as a None address argument in appropriate operation call

    # Block Move addressing: "blk" (2 opcodes) modeled inline

    # http://www.6502.org/tutorials/65c816opcodes.html#5.7 through 
    # http://www.6502.org/tutorials/65c816opcodes.html#5.9
    # discuss wrapping at $00ffff.  Since address modes simply return an
    # address the individual operations will need to handle any wrapping
    # differences (may need a wrap flag passed from the instruction, such as
    # opORA(self.DirectPageAddr, wrapFlag=1) to indicate the address returned
    # by DirectPageAddr needs to be wrapped in certain instances)
    # I would like to verify that the conditions specified in the link above
    # hold before spending the effort to code this

    # Possible affect on cycle counts:
    # When drp starts on a page boundary, the effective address is formed
    # by concatenating the dpr high byte to the direct page offset rather
    #  than simply adding drp and the offset, or:
    #
    #   (self.dpr >> self.BYTE_WIDTH) + self.ByteAt(epc)
    # vs
    #   self.dpr + self.ByteAt(epc)
    #
    # See 65816 Programming Manual, pg 156, which states that this save 1 cycle

    def DirectPageAddr(self): # "dpg" (24 opcodes)
        return (self.dpr + self.OperandByte()) & self.addrMask

    def DirectPageXAddr(self): # "dpx" (18 opcodes)
        return (self.dpr + self.OperandByte() + self.x) & self.addrMask

    def DirectPageYAddr(self): # "dpy" (2 opcodes)
        return (self.dpr + self.OperandByte() + self.y) & self.addrMask

    def DirectPageIndirectXAddr(self): # "dix" (8 opcodes)
        # *** TODO: verify WrapAt works correctly at $ffff ***
#        dpaddr = self.WrapAt((self.dpr + self.x + self.OperandByte()) & self.addrMask)
        dpaddr = (self.dpr + self.x + self.OperandByte()) & self.addrMask
        inaddr = self.WrapAt(dpaddr)
        return (self.dbr << self.ADDR_WIDTH) + inaddr

    def DirectPageIndirectAddr(self): # "dpi" (8 opcodes)
        # *** TODO: verify WrapAt works correctly at $ffff ***
        dpaddr = (self.dpr + self.OperandByte()) & self.addrMask
        inaddr = self.WrapAt(dpaddr)
        return (self.dbr << self.ADDR_WIDTH) + inaddr

    def DirectPageIndirectLongAddr(self): # new to 65816, "dil" (8 opcodes)
        # *** TODO: check on if need wrap at $ffff (seems likely) ***
        dpaddr = (self.dpr + self.OperandByte()) & self.addrMask
        addr = (self.ByteAt(dpaddr + 2) << self.ADDR_WIDTH) + self.WordAt(dpaddr)
        return addr

    def DirectPageIndirectYAddr(self): # "diy" (8 opcodes)
        # *** TODO: verify WrapAt works correctly at $ffff ***
#        dpaddr = self.WrapAt((self.dpr + self.OperandByte()) & self.addrMask)
#        a1 = (self.dbr << self.ADDR_WIDTH) + dpaddr
#        a2 = a1 + self.y
        dpaddr = (self.dpr + self.OperandByte()) & self.addrMask
        #inaddr = self.WrapAt(dpaddr)
        inaddr = self.WordAt(dpaddr)
        efaddr = (self.dbr << self.ADDR_WIDTH) + inaddr + self.y
        if self.addcycles:
            if (inaddr & self.addrBankMask) != (efaddr & self.addrBankMask):
                self.excycles += 1
        return efaddr

    def DirectPageIndirectLongYAddr(self): # new to 65816, "dly" (8 opcodes)
        # *** TODO: verify WrapAt works correctly at $ffff ***
#        dpaddr = self.WrapAt((self.dpr + self.OperandByte()) & self.addrMask)
#        dpaddr = self.WordAt((self.dpr + self.OperandByte()) & self.addrMask)
#        a1 = (self.ByteAt(dpaddr + 2) << self.ADDR_WIDTH) + dpaddr
#        a2 = a1 + self.y
        dpaddr = (self.dpr + self.OperandByte()) & self.addrMask
        inaddr = (self.ByteAt(dpaddr + 2) << self.ADDR_WIDTH) + self.WordAt(dpaddr)
        efaddr = inaddr + self.y
        if self.addcycles:
            if (inaddr & self.addrBankMask) != (efaddr & self.addrBankMask):
                self.excycles += 1
        return efaddr

    def ImmediateAddr(self): # "imm" (14 opcodes)
        return self.OperandAddr()

    # Implied addressing "imp" (29 opcodes, 65816 programming manual misses WAI)

    def ProgramCounterRelAddr(self): # "pcr" (9 opcodes)
        self.excycles += 1
        offset = self.OperandByte()
        self.incPC()

        if offset & self.NEGATIVE:
            addr = self.pc - (offset ^ self.byteMask) - 1
        else:
            addr = self.pc + offset

        # *** TODO: verify this extra cycle ***
        if (self.pc & self.addrHighMask) != (addr & self.addrHighMask):
            self.excycles += 1

        self.pc = (self.pbr << self.ADDR_WIDTH) + addr & self.addrMask

    def ProgramCounterRelLongAddr(self): # "prl" (1 opcode)
        self.excycles += 1
        offset = self.OperandWord()
        self.incPC()

        if (offset >> self.BYTE_WIDTH) & self.NEGATIVE:
            addr = self.pc - (offset ^ self.addrMask) - 1
        else:
            addr = self.pc + offset

        # *** TODO: verify this extra cycle ***
        if (self.pc & self.addrHighMask) != (addr & self.addrHighMask):
            self.excycles += 1

        self.pc = (self.pbr << self.ADDR_WIDTH) + addr & self.addrMask

    # Stack Absolute Addressing "ska" (1 opcode) modeled directly
    # Stack Direct Page Indirect Addressing "ski" (1 opcode) modeled directly
    # Stack Interrupt Addressing "stk" (2 opcodes) modeled directly
    # Stack Program Counter Relative Addressing "spc" (1 opcode) modeled directly
    # Stack Pull Addressing "stk" (6 opcodes) modeled directly
    # Stack Push Addressing "stk" (7 opcodes) modeled directly 65816 Programming manual only lists 6
    # Stack RTI, RTL, RTS Addressing "stk" (3 opcodes) modeled directly

    def StackRelAddr(self): # "str" (8 opcode) 65816 Programming manual only lists 4
        return (self.sp + self.OperandByte()) & self.addrMask

    def StackRelIndirectYAddr(self): # "siy" (8 opcode)
        # *** TODO: does this need WrapAt? ***
#        return (self.dbr << self.ADDR_WIDTH) + self.WordAt((self.sp + self.OperandByte()) & self.addrMask) + self.y
        spaddr = (self.sp + self.OperandByte()) & self.addrMask
        #inaddr = self.WrapAt(spaddr)
        inaddr = self.WordAt(spaddr)
        # *** TODO: any extra cycles? ***
        return (self.dbr << self.ADDR_WIDTH) + inaddr + self.y

    # operations

    def opADC(self, x):
        if self.p & self.MS:
            data = self.ByteAt(x())
        else:
            data = self.WordAt(x())

        if self.p & self.DECIMAL:
            # *** TODO: more to do here ***
            halfcarry = 0
            decimalcarry = 0
            adjust0 = 0
            adjust1 = 0
            nibble0 = (data & 0xf) + (self.a & 0xf) + (self.p & self.CARRY)
            if nibble0 > 9:
                adjust0 = 6
                halfcarry = 1
            nibble1 = ((data >> 4) & 0xf) + ((self.a >> 4) & 0xf) + halfcarry
            if nibble1 > 9:
                adjust1 = 6
                decimalcarry = 1

            # the ALU outputs are not decimally adjusted
            nibble0 = nibble0 & 0xf
            nibble1 = nibble1 & 0xf
            aluresult = (nibble1 << 4) + nibble0

            # the final A contents will be decimally adjusted
            nibble0 = (nibble0 + adjust0) & 0xf
            nibble1 = (nibble1 + adjust1) & 0xf
            self.p &= ~(self.CARRY | self.OVERFLOW | self.NEGATIVE | self.ZERO)
            if aluresult == 0:
                self.p |= self.ZERO
            else:
                self.p |= aluresult & self.NEGATIVE
            if decimalcarry == 1:
                self.p |= self.CARRY
            if (~(self.a ^ data) & (self.a ^ aluresult)) & self.NEGATIVE:
                self.p |= self.OVERFLOW
            self.a = (nibble1 << 4) + nibble0
        else:
            if self.p & self.CARRY:
                tmp = 1
            else:
                tmp = 0
            result = data + self.a + tmp
            self.p &= ~(self.CARRY | self.OVERFLOW | self.NEGATIVE | self.ZERO)

            if self.p & self.MS:
                if (~(self.a ^ data) & (self.a ^ result)) & self.NEGATIVE:
                    self.p |= self.OVERFLOW
            else:
                if (~(self.a ^ data) & (self.a ^ result)) & (self.NEGATIVE << self.BYTE_WIDTH):
                    self.p |= self.OVERFLOW
            data = result
            if self.p & self.MS:
                if data > self.byteMask:
                    self.p |= self.CARRY
                    data &= self.byteMask
            else:
                if data > self.addrMask:
                    self.p |= self.CARRY
                    data &= self.addrMask
            if data == 0:
                self.p |= self.ZERO
            else:
                if self.p & self.MS:
                    self.p |= data & self.NEGATIVE
                else:
                    self.p |= (data >> self.BYTE_WIDTH) & self.NEGATIVE
            self.a = data

    def opAND(self, x):
        if self.p & self.MS:
            self.a &= self.ByteAt(x())
            self.FlagsNZ(self.a)
        else:
            self.a &= self.WordAt(x())
            self.FlagsNZWord(self.a)

    def opASL(self, x):
        if x is None:
            tbyte = self.a
        else:
            addr = x()
            if self.p & self.MS:
                tbyte = self.ByteAt(addr)
            else:
                tbyte = self.WordAt(addr)

        self.p &= ~(self.CARRY | self.NEGATIVE | self.ZERO)

        if self.p & self.MS:
            if tbyte & self.NEGATIVE:
                self.p |= self.CARRY
            tbyte = (tbyte << 1) & self.byteMask
        else:
            if (tbyte >> self.BYTE_WIDTH) & self.NEGATIVE:
                self.p |= self.CARRY
            tbyte = (tbyte << 1) & self.addrMask

        if tbyte:
            if tbyte & self.NEGATIVE:
                self.p |= tbyte & self.NEGATIVE
            else:
                self.p |= (tbyte >> self.BYTE_WIDTH) & self.NEGATIVE
        else:
            self.p |= self.ZERO

        if x is None:
            self.a = tbyte
        else:
            if self.p & self.MS:
                self.memory[addr] = tbyte
            else:
                self.memory[addr] = tbyte & self.byteMask
                self.memory[addr+1] = tbyte >> self.BYTE_WIDTH

    def opBIT(self, x):
        if self.p & self.MS:
            tbyte = self.ByteAt(x())
        else:
            tbyte = self.WordAt(x())
            
        self.p &= ~(self.ZERO | self.NEGATIVE | self.OVERFLOW)
        if (self.a & tbyte) == 0:
            self.p |= self.ZERO
        if self.p & self.MS:
            self.p |= tbyte & (self.NEGATIVE | self.OVERFLOW)
        else:
            self.p |= (tbyte >> self.BYTE_WIDTH) & (self.NEGATIVE | self.OVERFLOW)

    def opCMP(self, addr, register_value, bit_flag):
        if self.p & bit_flag:
            tbyte = self.ByteAt(addr())
        else:
            tbyte = self.WordAt(addr())
        self.p &= ~(self.CARRY | self.ZERO | self.NEGATIVE)
        if register_value == tbyte:
            self.p |= self.CARRY | self.ZERO
        elif register_value > tbyte:
            self.p |= self.CARRY
        if self.p & bit_flag:
            self.p |= (register_value - tbyte) & self.NEGATIVE
        else:
            self.p |= ((register_value - tbyte) >> self.BYTE_WIDTH) & self.NEGATIVE

    def opDECR(self, x):
        if x is None:
            tbyte = self.a
        else:
            addr = x()
            if self.p & self.MS:
                tbyte = self.ByteAt(addr)
            else:
                tbyte = self.WordAt(addr)

        self.p &= ~(self.ZERO | self.NEGATIVE)
        if self.p & self.MS:
            tbyte = (tbyte - 1) & self.byteMask
        else:
            tbyte = (tbyte - 1) & self.addrMask
        if tbyte:
            if self.p & self.MS:
                self.p |= tbyte & self.NEGATIVE
            else:
                self.p |= (tbyte >> self.BYTE_WIDTH) & self.NEGATIVE
        else:
            self.p |= self.ZERO

        if x is None:
            self.a = tbyte
        else:
            if self.p & self.MS:
                self.memory[addr] = tbyte & self.byteMask
            else:
                self.memory[addr] = tbyte & self.byteMask
                self.memory[addr+1] = (tbyte >> self.BYTE_WIDTH)

    def opEOR(self, x):
        if self.p & self.MS:
            self.a ^= self.ByteAt(x())
            self.FlagsNZ(self.a)
        else:
            self.a ^= self.WordAt(x())
            self.FlagsNZWord(self.a)

    def opINCR(self, x):
        if x is None:
            tbyte = self.a
        else:
            addr = x()
            if self.p & self.MS:
                tbyte = self.ByteAt(addr)
            else:
                tbyte = self.WordAt(addr)

        self.p &= ~(self.ZERO | self.NEGATIVE)
        if self.p & self.MS:
            tbyte = (tbyte + 1) & self.byteMask
        else:
            tbyte = (tbyte + 1) & self.addrMask
        if tbyte:
            if self.p & self.MS:
                self.p |= tbyte & self.NEGATIVE
            else:
                self.p |= (tbyte >> self.BYTE_WIDTH) & self.NEGATIVE
        else:
            self.p |= self.ZERO

        if x is None:
            self.a = tbyte
        else:
            if self.p & self.MS:
                self.memory[addr] = tbyte & self.byteMask
            else:
                self.memory[addr] = tbyte & self.byteMask
                self.memory[addr+1] = (tbyte >> self.BYTE_WIDTH)

    def opLDA(self, x):
        if self.p & self.MS:
            self.a = self.ByteAt(x())
            self.FlagsNZ(self.a)
        else:
            self.a = self.WordAt(x())
            self.FlagsNZWord(self.a)

    def opLDX(self, y):
        if self.p & self.IRS:
            self.x = self.ByteAt(y())
            self.FlagsNZ(self.x)
        else:
            self.x = self.WordAt(y())
            self.FlagsNZWord(self.x)

    def opLDY(self, x):
        if self.p & self.IRS:
            self.y = self.ByteAt(x())
            self.FlagsNZ(self.y)
        else:
            self.y = self.WordAt(x())
            self.FlagsNZWord(self.y)

    def opLSR(self, x):
        if x is None:
            tbyte = self.a
        else:
            addr = x()
            if self.p & self.MS:
                tbyte = self.ByteAt(addr)
            else:
                tbyte = self.WordAt(addr)

        self.p &= ~(self.CARRY | self.NEGATIVE | self.ZERO)
        self.p |= tbyte & 1

        tbyte = tbyte >> 1
        if tbyte:
            pass
        else:
            self.p |= self.ZERO

        if x is None:
            self.a = tbyte
        else:
            if self.p & self.MS:
                self.memory[addr] = tbyte
            else:
                self.memory[addr] = tbyte & self.byteMask
                self.memory[addr+1] = tbyte >> self.BYTE_WIDTH

    def opMVB(self, inc):
        # X is source, Y is dest, A is bytes to move - 1
        # If inc = 1 the addresses are the start
        # If inc = -1 the addresses are the end
        # Operand lsb is dest dbr, msb is source
        dbr = self.OperandByte() << self.ADDR_WIDTH
        sbr = (self.OperandWord() >> self.BYTE_WIDTH) << self.ADDR_WIDTH
        self.memory[dbr + self.y] = self.memory[sbr + self.x]
        self.x += inc
        self.y += inc
        if self.p & self.IRS:
            self.x &= self.byteMask
            self.y &= self.byteMask
        else:
            self.x &= self.addrMask
            self.y &= self.addrMask

        if self.p & self.MS:
            c = (self.b << self.BYTE_WIDTH) + self.a - 1
            self.a = c & self.byteMask
            self.b = (c >> self.BYTE_WIDTH) & self.byteMask
        else:
            self.a -= 1
            self.a &= self.addrMask

    def opORA(self, x):
        if self.p & self.MS:
            self.a |= self.ByteAt(x())
            self.FlagsNZ(self.a)
        else:
            self.a |= self.WordAt(x())
            self.FlagsNZWord(self.a)

    def opROL(self, x):
        if x is None:
            tbyte = self.a
        else:
            addr = x()
            if self.p & self.MS:
                tbyte = self.ByteAt(addr)
            else:
                tbyte = self.WordAt(addr)

        if self.p & self.CARRY:
            if self.p & self.MS:
                if tbyte & self.NEGATIVE:
                    pass
                else:
                    self.p &= ~self.CARRY
            else:
                if (tbyte >> self.BYTE_WIDTH) & self.NEGATIVE:
                    pass
                else:
                    self.p &= ~self.CARRY

            tbyte = (tbyte << 1) | 1
        else:
            if self.p & self.MS:
                if tbyte & self.NEGATIVE:
                    self.p |= self.CARRY
            else:
                if (tbyte >> self.BYTE_WIDTH) & self.NEGATIVE:
                    self.p |= self.CARRY
            tbyte = tbyte << 1

        if self.p & self.MS:
            tbyte &= self.byteMask
            self.FlagsNZ(tbyte)
        else:
            tbyte &= self.addrMask
            self.FlagsNZWord(tbyte)

        if x is None:
            self.a = tbyte
        else:
            if self.p & self.MS:
                self.memory[addr] = tbyte & self.byteMask
            else:
                self.memory[addr] = tbyte & self.byteMask
                self.memory[addr+1] = tbyte >> self.BYTE_WIDTH

    def opROR(self, x):
        if x is None:
            tbyte = self.a
        else:
            addr = x()
            if self.p & self.MS:
                tbyte = self.ByteAt(addr)
            else:
                tbyte = self.WordAt(addr)

        if self.p & self.CARRY:
            if tbyte & 1:
                pass
            else:
                self.p &= ~self.CARRY
            if self.p & self.MS:
                tbyte = (tbyte >> 1) | self.NEGATIVE
            else:
                tbyte = (tbyte >> 1) | (self.NEGATIVE << self.BYTE_WIDTH)
        else:
            if tbyte & 1:
                self.p |= self.CARRY
            tbyte = tbyte >> 1

        if self.p & self.MS:
            self.FlagsNZ(tbyte)
        else:
            self.FlagsNZWord(tbyte)

        if x is None:
            self.a = tbyte
        else:
            if self.p & self.MS:
                self.memory[addr] = tbyte & self.byteMask
            else:
                self.memory[addr] = tbyte & self.byteMask
                self.memory[addr+1] = tbyte >> self.BYTE_WIDTH

    def opSBC(self, x):
        if self.p & self.MS:
            data = self.ByteAt(x())
        else:
            data = self.WordAt(x())

        if self.p & self.DECIMAL:
            # *** TODO: more to do here ***
            halfcarry = 1
            decimalcarry = 0
            adjust0 = 0
            adjust1 = 0

            nibble0 = (self.a & 0xf) + (~data & 0xf) + (self.p & self.CARRY)
            if nibble0 <= 0xf:
                halfcarry = 0
                adjust0 = 10
            nibble1 = ((self.a >> 4) & 0xf) + ((~data >> 4) & 0xf) + halfcarry
            if nibble1 <= 0xf:
                adjust1 = 10 << 4

            # the ALU outputs are not decimally adjusted
            aluresult = self.a + (~data & self.byteMask) + \
                (self.p & self.CARRY)

            if aluresult > self.byteMask:
                decimalcarry = 1
            aluresult &= self.byteMask

            # but the final result will be adjusted
            nibble0 = (aluresult + adjust0) & 0xf
            nibble1 = ((aluresult + adjust1) >> 4) & 0xf

            self.p &= ~(self.CARRY | self.ZERO | self.NEGATIVE | self.OVERFLOW)
            if aluresult == 0:
                self.p |= self.ZERO
            else:
                self.p |= aluresult & self.NEGATIVE
            if decimalcarry == 1:
                self.p |= self.CARRY
            if ((self.a ^ data) & (self.a ^ aluresult)) & self.NEGATIVE:
                self.p |= self.OVERFLOW
            self.a = (nibble1 << 4) + nibble0
        else:
            if self.p & self.MS:
                result = self.a + (~data & self.byteMask) + (self.p & self.CARRY)
            else:
                result = self.a + (~data & self.addrMask) + (self.p & self.CARRY)
            self.p &= ~(self.CARRY | self.ZERO | self.OVERFLOW | self.NEGATIVE)
            if self.p & self.MS:
                if ((self.a ^ data) & (self.a ^ result)) & self.NEGATIVE:
                    self.p |= self.OVERFLOW
                data = result & self.byteMask
                if result > self.byteMask:
                    self.p |= self.CARRY
                self.p |= data & self.NEGATIVE
            else:
                if (((self.a ^ data) & (self.a ^ result)) >> self.BYTE_WIDTH) & self.NEGATIVE:
                    self.p |= self.OVERFLOW
                data = result & self.addrMask
                if result > self.addrMask:
                    self.p |= self.CARRY
                self.p |= (data >> self.BYTE_WIDTH) & self.NEGATIVE
            if data == 0:
                self.p |= self.ZERO

            self.a = data

    def opSTA(self, x):
        addr = x()
        if self.p & self.MS:
            self.memory[addr] = self.a & self.byteMask
        else:
            self.memory[addr] = self.a & self.byteMask
            self.memory[addr+1] = (self.a >> self.BYTE_WIDTH) & self.byteMask

    # *** TODO: do we really need this here? can x/y MSB be non-zero when IRS is 1? ***
    def opSTX(self, y):
        addr = y()
        if self.p & self.IRS:
            self.memory[addr] = self.x & self.byteMask
        else:
            self.memory[addr] = self.x & self.byteMask
            self.memory[addr+1] = (self.x >> self.BYTE_WIDTH) & self.byteMask

    # *** TODO: do we really need this here? can x/y MSB be non-zero when IRS is 1? ***
    def opSTY(self, x):
        addr = x()
        if self.p & self.IRS:
            self.memory[addr] = self.y & self.byteMask
        else:
            self.memory[addr] = self.y & self.byteMask
            self.memory[addr+1] = (self.y >> self.BYTE_WIDTH) & self.byteMask

    def opSTZ(self, x):
        addr = x()
        if self.p & self.IRS:
            self.memory[addr] = 0x00
        else:
            self.memory[addr] = 0x00
            self.memory[addr+1] = 0x00

    def opTSB(self, x):
        addr = x()
        if self.p & self.MS:
            m = self.memory[addr]
        else:
            m = (self.memory[addr+1] << self.BYTE_WIDTH) + self.memory[addr]

        self.p &= ~self.ZERO
        z = m & self.a
        if z == 0:
            self.p |= self.ZERO

        r = m | self.a
        if self.p & self.MS:
            self.memory[addr] = r
        else:
            self.memory[addr] = r & self.byteMask
            self.memory[addr+1] = (r >> self.BYTE_WIDTH) & self.byteMask

    def opTRB(self, x):
        addr = x()
        if self.p & self.MS:
            m = self.memory[addr]
        else:
            m = (self.memory[addr+1] << self.BYTE_WIDTH) + self.memory[addr]

        self.p &= ~self.ZERO
        z = m & self.a
        if z == 0:
            self.p |= self.ZERO

        r = m & ~self.a
        if self.p & self.MS:
            self.memory[addr] = r
        else:
            self.memory[addr] = r & self.byteMask
            self.memory[addr+1] = (r >> self.BYTE_WIDTH) & self.byteMask

    # instructions

    # the 65816 implements all opcodes
    instruct = [0] * 256
    cycletime = [0] * 256
    extracycles = [0] * 256
    disassemble = [0] * 256

    instruction = make_instruction_decorator(instruct, disassemble,
                                             cycletime, extracycles)

    # *** TODO: extra cycles need considered for all new to 65816 only opcodes ***
    @instruction(name="BRK", mode="stk", cycles=7)
    def inst_0x00(self):
        if not self.mode:
            self.stPush(self.pbr)

        # pc has already been increased one
        # increment for optional signature byte
        pc = (self.pc + 1) & self.addrMask
        self.stPushWord(pc)

        if self.mode:
            self.p |= self.BREAK
            self.stPush(self.p | self.BREAK | self.UNUSED)
        else:
            self.stPush(self.p)

        self.p |= self.INTERRUPT
        self.pbr = 0
        if self.mode:
            self.pc = self.WordAt(self.IRQ[self.mode])
        else:
            self.pc = self.WordAt(self.BRK)

        # 65C816 clears decimal flag, NMOS 6502 does not
        self.p &= ~self.DECIMAL

    @instruction(name="ORA", mode="dix", cycles=6)
    def inst_0x01(self):
        self.opORA(self.DirectPageIndirectXAddr)
        self.incPC()

    @instruction(name="COP", mode="stk", cycles=7)  # new to 65816
    def inst_0x02(self):
        # *** TODO: consider consolidating with BRK ***
        if not self.mode:
            self.stPush(self.pbr)

        # pc has already been increased one
        # increment for optional signature byte
        pc = (self.pc + 1) & self.addrMask
        self.stPushWord(pc)

        self.stPush(self.p)

        self.p |= self.INTERRUPT
        self.pbr = 0
        self.pc = self.WordAt(self.COP[self.mode])

        # 65C816 clears decimal flag
        self.p &= ~self.DECIMAL

    @instruction(name="ORA", mode="str", cycles=2)  # new to 65816
    def inst_0x03(self):
        self.opORA(self.StackRelAddr)
        self.incPC()

    @instruction(name="TSB", mode="dpg", cycles=5)
    def inst_0x04(self):
        self.opTSB(self.DirectPageAddr)
        self.incPC()

    @instruction(name="ORA", mode="dpg", cycles=3)
    def inst_0x05(self):
        self.opORA(self.DirectPageAddr)
        self.incPC()

    @instruction(name="ASL", mode="dpg", cycles=5)
    def inst_0x06(self):
        self.opASL(self.DirectPageAddr)
        self.incPC()

    @instruction(name="ORA", mode="dil", cycles=6)  # new to 65816
    def inst_0x07(self):
        self.opORA(self.DirectPageIndirectLongAddr)
        self.incPC()

    @instruction(name="PHP", mode="stk", cycles=3)
    def inst_0x08(self):
        if self.mode:
            self.stPush(self.p | self.BREAK | self.UNUSED)
        else:
            self.stPush(self.p)

    @instruction(name="ORA", mode="imm", cycles=2)
    def inst_0x09(self):
        self.opORA(self.ImmediateAddr)
        self.incPC(2 - ((self.p & self.MS)>>5))

    @instruction(name="ASL", mode="acc", cycles=2)
    def inst_0x0a(self):
        self.opASL(None)

    @instruction(name="PHD", mode="stk", cycles=4) # new to 65816
    def inst_0x0b(self):
        self.stPushWord(self.dpr)

    @instruction(name="TSB", mode="abs", cycles=6)
    def inst_0x0c(self):
        self.opTSB(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="ORA", mode="abs", cycles=4)
    def inst_0x0d(self):
        self.opORA(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="ASL", mode="abs", cycles=6)
    def inst_0x0e(self):
        self.opASL(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="ORA", mode="abl", cycles=5) # new to 65816
    def inst_0x0f(self):
        self.opORA(self.AbsoluteLongAddr)
        self.incPC(3)

    @instruction(name="BPL", mode="pcr", cycles=2, extracycles=2)
    def inst_0x10(self):
        self.bCLR(self.NEGATIVE)

    @instruction(name="ORA", mode="diy", cycles=5, extracycles=1)
    def inst_0x11(self):
        self.opORA(self.DirectPageIndirectYAddr)
        self.incPC()

    @instruction(name="ORA", mode="dpi", cycles=5)
    def inst_0x12(self):
        self.opORA(self.DirectPageIndirectAddr)
        self.incPC()

    @instruction(name="ORA", mode="siy", cycles=7) # new to 65816
    def inst_0x13(self):
        self.opORA(self.StackRelIndirectYAddr)
        self.incPC()

    @instruction(name="TRB", mode="dpg", cycles=5)
    def inst_0x14(self):
        self.opTRB(self.DirectPageAddr)
        self.incPC()

    @instruction(name="ORA", mode="dpx", cycles=4)
    def inst_0x15(self):
        self.opORA(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="ASL", mode="dpx", cycles=6)
    def inst_0x16(self):
        self.opASL(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="ORA", mode="dly", cycles=6)  # new to 65816
    def inst_0x17(self):
        self.opORA(self.DirectPageIndirectLongYAddr)
        self.incPC()

    @instruction(name="CLC", mode="imp", cycles=2)
    def inst_0x18(self):
        self.pCLR(self.CARRY)

    @instruction(name="ORA", mode="aby", cycles=4, extracycles=1)
    def inst_0x19(self):
        self.opORA(self.AbsoluteYAddr)
        self.incPC(2)

    @instruction(name="INC", mode="acc", cycles=2)
    def inst_0x1a(self):
        self.opINCR(None)

    @instruction(name="TCS", mode="imp", cycles=2) # new to 65816
    def inst_0x1b(self):
        if self.p & self.MS:
            # A is 8 bit
            if self.mode:
                # high byte is forced to 1 elsewhere
                self.sp = self.a & self.byteMask
            else:
                # hidden B is transfered
                self.sp = (self.b << self.BYTE_WIDTH) + self.a
        else:
            # A is 16 bit
            self.sp = self.a

    @instruction(name="TRB", mode="abs", cycles=6)
    def inst_0x1c(self):
        self.opTRB(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="ORA", mode="abx", cycles=4, extracycles=1)
    def inst_0x1d(self):
        self.opORA(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="ASL", mode="abx", cycles=7)
    def inst_0x1e(self):
        self.opASL(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="ORA", mode="alx", cycles=5) # new to 65816
    def inst_0x1f(self):
        self.opORA(self.AbsoluteLongXAddr)
        self.incPC(3)

    @instruction(name="JSR", mode="abs", cycles=6)
    def inst_0x20(self):
        self.stPushWord((self.pc + 1) & self.addrMask)
        self.pc = self.OperandWord()

    @instruction(name="AND", mode="dix", cycles=6)
    def inst_0x21(self):
        self.opAND(self.DirectPageIndirectXAddr)
        self.incPC()

    @instruction(name="JSL", mode="abl", cycles=8) # new to 65816
    def inst_0x22(self):
        self.stPush(self.pbr)
        self.stPushWord((self.pc + 2) & self.addrMask)
        self.pbr = self.ByteAt(self.pc + 2)
        self.pc = self.OperandWord()

    @instruction(name="AND", mode="str", cycles=4) # new to 65816
    def inst_0x23(self):
        self.opAND(self.StackRelAddr)
        self.incPC()

    @instruction(name="BIT", mode="dpg", cycles=3)
    def inst_0x24(self):
        self.opBIT(self.DirectPageAddr)
        self.incPC()

    @instruction(name="AND", mode="dpg", cycles=3)
    def inst_0x25(self):
        self.opAND(self.DirectPageAddr)
        self.incPC()

    @instruction(name="ROL", mode="dpg", cycles=5)
    def inst_0x26(self):
        self.opROL(self.DirectPageAddr)
        self.incPC()

    @instruction(name="AND", mode="dil", cycles=6)  # new to 65816
    def inst_0x27(self):
        self.opAND(self.DirectPageIndirectLongAddr)
        self.incPC()

    @instruction(name="PLP", mode="stk", cycles=4)
    def inst_0x28(self):
        p = self.stPop()
        if self.mode:
            self.p = p | self.BREAK | self.UNUSED
        else:
            if p & self.MS != self.p & self.MS:
                if p & self.MS:
                    # A 16 => 8, save B, mask off high byte of A
                    self.b = (self.a >> self.BYTE_WIDTH) & self.byteMask
                    self.a = self.a & self.byteMask
                else:
                    # A 8 => 16, set A = b a
                    self.a = (self.b << self.BYTE_WIDTH) + self.a
                    self.b = 0
            if p & self.IRS != self.p & self.IRS:
                if self.p & self.IRS:
                    # X,Y 16 => 8, truncate X,Y
                    self.x = self.x & self.byteMask
                    self.y = self.y & self.byteMask
            self.p = p

    @instruction(name="AND", mode="imm", cycles=2)
    def inst_0x29(self):
        self.opAND(self.ImmediateAddr)
        self.incPC(2 - ((self.p & self.MS)>>5))

    @instruction(name="ROL", mode="acc", cycles=2)
    def inst_0x2a(self):
        self.opROL(None)

    @instruction(name="PLD", mode="stk", cycles=5) # new to 65816
    def inst_0x2b(self):
        self.dpr = self.stPopWord()

    @instruction(name="BIT", mode="abs", cycles=4)
    def inst_0x2c(self):
        self.opBIT(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="AND", mode="abs", cycles=4)
    def inst_0x2d(self):
        self.opAND(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="ROL", mode="abs", cycles=6)
    def inst_0x2e(self):
        self.opROL(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="AND", mode="abl", cycles=5) # new to 65816
    def inst_0x2f(self):
        self.opAND(self.AbsoluteLongAddr)
        self.incPC(3)

    @instruction(name="BMI", mode="pcr", cycles=2, extracycles=2)
    def inst_0x30(self):
        self.bSET(self.NEGATIVE)

    @instruction(name="AND", mode="diy", cycles=5, extracycles=1)
    def inst_0x31(self):
        self.opAND(self.DirectPageIndirectYAddr)
        self.incPC()

    @instruction(name="AND", mode="dpi", cycles=5)
    def inst_0x32(self):
        self.opAND(self.DirectPageIndirectAddr)
        self.incPC()

    @instruction(name="AND", mode="siy", cycles=7) # new to 65816
    def inst_0x33(self):
        self.opAND(self.StackRelIndirectYAddr)
        self.incPC()

    @instruction(name="BIT", mode="dpx", cycles=4)
    def inst_0x34(self):
        self.opBIT(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="AND", mode="dpx", cycles=4)
    def inst_0x35(self):
        self.opAND(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="ROL", mode="dpx", cycles=6)
    def inst_0x36(self):
        self.opROL(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="AND", mode="dly", cycles=7) # new to 65816
    def inst_0x37(self):
        self.opAND(self.DirectPageIndirectLongYAddr)
        self.incPC()

    @instruction(name="SEC", mode="imp", cycles=2)
    def inst_0x38(self):
        self.pSET(self.CARRY)

    @instruction(name="AND", mode="aby", cycles=4, extracycles=1)
    def inst_0x39(self):
        self.opAND(self.AbsoluteYAddr)
        self.incPC(2)

    @instruction(name="DEC", mode="acc", cycles=2)
    def inst_0x3a(self):
        self.opDECR(None)

    @instruction(name="TSC", mode="imp", cycles=2) # new to 65816
    def inst_0x3b(self):
        if self.p & self.MS:
            # A is 8 bit, hidden B is set to high byte
            if self.mode:
                self.b = 0x01
            else:
                self.b = self.sp >> self.BYTE_WIDTH
            self.a = self.sp & self.byteMask
        else:
            # A is 16 bit
            self.a = self.sp

        self.FlagsNZWord(self.sp)

    @instruction(name="BIT", mode="abx", cycles=4)
    def inst_0x3c(self):
        self.opBIT(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="AND", mode="abx", cycles=4, extracycles=1)
    def inst_0x3d(self):
        self.opAND(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="ROL", mode="abx", cycles=7)
    def inst_0x3e(self):
        self.opROL(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="AND", mode="alx", cycles=5) # new to 65816
    def inst_0x3f(self):
        self.opAND(self.AbsoluteLongXAddr)
        self.incPC(3)

    @instruction(name="RTI", mode="stk", cycles=6)
    def inst_0x40(self):
        # *** TODO: should this be similar to PLP? ***
        if self.mode:
            self.p = (self.stPop() | self.BREAK | self.UNUSED)
            self.pc = self.stPopWord()
        else:
            self.p = self.stPop()
            self.pc = self.stPopWord()
            self.pbr = self.stPop()

    @instruction(name="EOR", mode="dix", cycles=6)
    def inst_0x41(self):
        self.opEOR(self.DirectPageIndirectXAddr)
        self.incPC()

    @instruction(name="WDM", mode="imp", cycles=2) # new to 65816
    def inst_0x42(self):
        # shouldn't be used but if this acts like a two byte NOP
        self.incPC()

    @instruction(name="EOR", mode="str", cycles=4) # new to 65816
    def inst_0x43(self):
        self.opEOR(self.StackRelAddr)
        self.incPC()

    @instruction(name="MVP", mode="blk", cycles=7) # new to 65816
    def inst_0x44(self):
        # MVP handles interrupts by not incrementing pc until C == $ffff
        # thus like the 65816 it completes the current byte transfer before
        # breaking for the interrupt and then returns
        # X is source, Y is dest ending addresses; A is bytes to move - 1 
        # Operand lsb is dest dbr, msb is source

        if self.p & self.MS:
            c = (self.b << self.BYTE_WIDTH) + self.a
        else:
            c = self.a

        if c != 0xffff:
            self.opMVB(-1)
            self.pc -= 1 # move pc back to the MVP instruction
        else:
            self.dbr = self.OperandByte()
            self.incPC(2)

    @instruction(name="EOR", mode="dpg", cycles=3)
    def inst_0x45(self):
        self.opEOR(self.DirectPageAddr)
        self.incPC()

    @instruction(name="LSR", mode="dpg", cycles=5)
    def inst_0x46(self):
        self.opLSR(self.DirectPageAddr)
        self.incPC()

    @instruction(name="EOR", mode="dil", cycles=6) # new to 65816
    def inst_0x47(self):
        self.opEOR(self.DirectPageIndirectLongAddr)
        self.incPC()

    @instruction(name="PHA", mode="stk", cycles=3)
    def inst_0x48(self):
        if self.p & self.MS:
            self.stPush(self.a)
        else:
            self.stPushWord(self.a)

    @instruction(name="EOR", mode="imm", cycles=2)
    def inst_0x49(self):
        self.opEOR(self.ImmediateAddr)
        self.incPC(2 - ((self.p & self.MS)>>5))

    @instruction(name="LSR", mode="acc", cycles=2)
    def inst_0x4a(self):
        self.opLSR(None)

    @instruction(name="PHK", mode="stk", cycles=3) # new to 65816
    def inst_0x4b(self):
        self.stPush(self.pbr)

    @instruction(name="JMP", mode="abs", cycles=3)
    def inst_0x4c(self):
        self.pc = self.OperandWord()


    @instruction(name="EOR", mode="abs", cycles=4)
    def inst_0x4d(self):
        self.opEOR(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="LSR", mode="abs", cycles=6)
    def inst_0x4e(self):
        self.opLSR(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="EOR", mode="abl", cycles=5) # new to 65816
    def inst_0x4f(self):
        self.opEOR(self.AbsoluteLongAddr)
        self.incPC(3)

    @instruction(name="BVC", mode="pcr", cycles=2, extracycles=2)
    def inst_0x50(self):
        self.bCLR(self.OVERFLOW)

    @instruction(name="EOR", mode="diy", cycles=5, extracycles=1)
    def inst_0x51(self):
        self.opEOR(self.DirectPageIndirectYAddr)
        self.incPC()

    @instruction(name="EOR", mode="dpi", cycles=5)
    def inst_0x52(self):
        self.opEOR(self.DirectPageIndirectAddr)
        self.incPC()

    @instruction(name="EOR", mode="siy", cycles=7) # new to 65816
    def inst_0x53(self):
        self.opEOR(self.StackRelIndirectYAddr)
        self.incPC()

    @instruction(name="MVN", mode="blk", cycles=7) # new to 65816
    def inst_0x54(self):
        # MVN handles interrupts by not incrementing pc until A == $ffff
        # thus like the 65816 it completes the current byte transfer before
        # breaking for the interrupt and then returns
        # X is source, Y is dest starting addresses; A is bytes to move - 1 
        # Operand lsb is dest dbr, msb is source

        if self.p & self.MS:
            c = (self.b << self.BYTE_WIDTH) + self.a
        else:
            c = self.a

        if c != 0xffff:
            self.opMVB(1)
            self.pc -= 1 # move pc back to the MVP instruction
        else:
            self.dbr = self.OperandByte()
            self.incPC(2)

    @instruction(name="EOR", mode="dpx", cycles=4)
    def inst_0x55(self):
        self.opEOR(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="LSR", mode="dpx", cycles=6)
    def inst_0x56(self):
        self.opLSR(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="EOR", mode="dly", cycles=6) # new to 65816
    def inst_0x57(self):
        self.opEOR(self.DirectPageIndirectLongYAddr)
        self.incPC()

    @instruction(name="CLI", mode="imp", cycles=2)
    def inst_0x58(self):
        self.pCLR(self.INTERRUPT)

    @instruction(name="EOR", mode="aby", cycles=4, extracycles=1)
    def inst_0x59(self):
        self.opEOR(self.AbsoluteYAddr)
        self.incPC(2)

    @instruction(name="PHY", mode="stk", cycles=3)
    def inst_0x5a(self):
        if self.p & self.IRS:
            self.stPush(self.y)
        else:
            self.stPushWord(self.y)

    @instruction(name="TCD", mode="imp", cycles=2) # new to 65816
    def inst_0x5b(self):
        if self.p & self.MS:
            # A is 8 bit, hidden B is transfered as well
            self.dpr = (self.b << self.BYTE_WIDTH) + self.a
        else:
            # A is 16 bit
            self.dpr = self.a

        self.FlagsNZWord(self.dpr)

    @instruction(name="JML", mode="abl", cycles=4)  # new to 65816
    def inst_0x5c(self):
        self.pbr = self.ByteAt(self.pc + 2)
        self.pc = self.OperandWord()

    @instruction(name="EOR", mode="abx", cycles=4, extracycles=1)
    def inst_0x5d(self):
        self.opEOR(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="LSR", mode="abx", cycles=7)
    def inst_0x5e(self):
        self.opLSR(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="EOR", mode="alx", cycles=5) # new to 65816
    def inst_0x5f(self):
        self.opEOR(self.AbsoluteLongXAddr)
        self.incPC(3)

    @instruction(name="RTS", mode="stk", cycles=6)
    def inst_0x60(self):
        self.pc = self.stPopWord()
        self.incPC()

    @instruction(name="ADC", mode="dix", cycles=6)
    def inst_0x61(self):
        self.opADC(self.DirectPageIndirectXAddr)
        self.incPC()

    @instruction(name="PER", mode="spc", cycles=6) # new to 65816
    def inst_0x62(self):
        self.stPushWord((self.pc + self.OperandWord()) & self.addrMask)
        self.incPC(2)

    @instruction(name="ADC", mode="str", cycles=4) # new to 65816
    def inst_0x63(self):
        self.opADC(self.StackRelAddr)
        self.incPC()

    @instruction(name="STZ", mode="dpg", cycles=3)
    def inst_0x64(self):
        self.opSTZ(self.DirectPageAddr)
        self.incPC()

    @instruction(name="ADC", mode="dpg", cycles=3)
    def inst_0x65(self):
        self.opADC(self.DirectPageAddr)
        self.incPC()

    @instruction(name="ROR", mode="dpg", cycles=5)
    def inst_0x66(self):
        self.opROR(self.DirectPageAddr)
        self.incPC()

    @instruction(name="ADC", mode="dil", cycles=6) # new to 65816
    def inst_0x67(self):
        self.opADC(self.DirectPageIndirectLongAddr)
        self.incPC()

    @instruction(name="PLA", mode="stk", cycles=4)
    def inst_0x68(self):
        if self.p & self.MS:
            self.a = self.stPop()
            self.FlagsNZ(self.a)
        else:
            self.a = self.stPopWord()
            self.FlagsNZWord(self.a)

    @instruction(name="ADC", mode="imm", cycles=2)
    def inst_0x69(self):
        self.opADC(self.ImmediateAddr)
        self.incPC(2 - ((self.p & self.MS)>>5))

    @instruction(name="ROR", mode="acc", cycles=2)
    def inst_0x6a(self):
        self.opROR(None)

    @instruction(name="RTL", mode="stk", cycles=6) # new to 65816
    def inst_0x6b(self):
        self.pc = self.stPopWord()
        self.pbr = self.stPop()
        self.incPC()

    @instruction(name="JMP", mode="abi", cycles=5)
    def inst_0x6c(self):
        # 65C02 and 65816 don't wrap
        self.pc = self.WordAt(self.AbsoluteIndirectAddr())

    @instruction(name="ADC", mode="abs", cycles=4)
    def inst_0x6d(self):
        self.opADC(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="ROR", mode="abs", cycles=6)
    def inst_0x6e(self):
        self.opROR(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="ADC", mode="abl", cycles=5) # new to 65816
    def inst_0x6f(self):
        self.opADC(self.AbsoluteLongAddr)
        self.incPC(3)

    @instruction(name="BVS", mode="pcr", cycles=2, extracycles=2)
    def inst_0x70(self):
        self.bSET(self.OVERFLOW)

    @instruction(name="ADC", mode="diy", cycles=5, extracycles=1)
    def inst_0x71(self):
        self.opADC(self.DirectPageIndirectYAddr)
        self.incPC()

    @instruction(name="ADC", mode="dpi", cycles=5)
    def inst_0x72(self):
        self.opADC(self.DirectPageIndirectAddr)
        self.incPC()

    @instruction(name="ADC", mode="siy", cycles=7) # new to 65816
    def inst_0x73(self):
        self.opADC(self.StackRelIndirectYAddr)
        self.incPC()

    @instruction(name="STZ", mode="dpx", cycles=4)
    def inst_0x74(self):
        self.opSTZ(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="ADC", mode="dpx", cycles=4)
    def inst_0x75(self):
        self.opADC(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="ROR", mode="dpx", cycles=6)
    def inst_0x76(self):
        self.opROR(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="ADC", mode="dly", cycles=6) # new to 65816
    def inst_0x77(self):
        self.opADC(self.DirectPageIndirectLongYAddr)
        self.incPC()

    @instruction(name="SEI", mode="imp", cycles=2)
    def inst_0x78(self):
        self.pSET(self.INTERRUPT)

    @instruction(name="ADC", mode="aby", cycles=4, extracycles=1)
    def inst_0x79(self):
        self.opADC(self.AbsoluteYAddr)
        self.incPC(2)

    @instruction(name="PLY", mode="stk", cycles=4)
    def inst_0x7a(self):
        if self.p & self.IRS:
            self.y = self.stPop()
            self.FlagsNZ(self.y)
        else:
            self.y = self.stPopWord()
            self.FlagsNZWord(self.y)

    @instruction(name="TDC", mode="imp", cycles=2) # new to 65816
    def inst_0x7b(self):
        if self.p & self.MS:
            # A is 8 bit, hidden B is set to high byte
            self.b = self.dpr >> self.BYTE_WIDTH
            self.a = self.dpr & self.byteMask
        else:
            # A is 16 bit
            self.a = self.dpr

        self.FlagsNZWord(self.dpr)

    @instruction(name="JMP", mode="aix", cycles=6)
    def inst_0x7c(self):
        self.pc = self.WordAt(self.AbsoluteIndirectXAddr())

    @instruction(name="ADC", mode="abx", cycles=4, extracycles=1)
    def inst_0x7d(self):
        self.opADC(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="ROR", mode="abx", cycles=7)
    def inst_0x7e(self):
        self.opROR(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="ADC", mode="alx", cycles=5) # new to 65816
    def inst_0x7F(self):
        self.opADC(self.AbsoluteLongXAddr)
        self.incPC(3)

    @instruction(name="BRA", mode="pcr", cycles=1, extracycles=1)
    def inst_0x80(self):
        self.ProgramCounterRelAddr()

    @instruction(name="STA", mode="dix", cycles=6)
    def inst_0x81(self):
        self.opSTA(self.DirectPageIndirectXAddr)
        self.incPC()

    @instruction(name="BRL", mode="prl", cycles=4) # new to 65816
    def inst_0x82(self):
        self.ProgramCounterRelLongAddr()

    @instruction(name="STA", mode="str", cycles=4) # new to 65816
    def inst_0x83(self):
        self.opSTA(self.StackRelAddr)
        self.incPC()

    @instruction(name="STY", mode="dpg", cycles=3)
    def inst_0x84(self):
        self.opSTY(self.DirectPageAddr)
        self.incPC()

    @instruction(name="STA", mode="dpg", cycles=3)
    def inst_0x85(self):
        self.opSTA(self.DirectPageAddr)
        self.incPC()

    @instruction(name="STX", mode="dpg", cycles=3)
    def inst_0x86(self):
        self.opSTX(self.DirectPageAddr)
        self.incPC()

    @instruction(name="STA", mode="dil", cycles=2) # new to 65816
    def inst_0x87(self):
        self.opSTA(self.DirectPageIndirectLongAddr)
        self.incPC()

    @instruction(name="DEY", mode="imp", cycles=2)
    def inst_0x88(self):
        self.y -= 1
        if self.p & self.IRS:
            self.y &= self.byteMask
            self.FlagsNZ(self.y)
        else:
            self.y &= self.addrMask
            self.FlagsNZWord(self.y)

    @instruction(name="BIT", mode="imm", cycles=2)
    def inst_0x89(self):
        # *** TODO: consider using op BIT using: ***
        #p = self.p
        #self.opBIT(self.ImmediateAddr)
        # This instruction (BIT #$12) does not use opBIT because in the
        # immediate mode, BIT only affects the Z flag.
        if self.p & self.MS:
            tbyte = self.OperandByte()
        else:
            tbyte = self.OperandWord()
        self.p &= ~(self.ZERO)
        if (self.a & tbyte) == 0:
            self.p |= self.ZERO
        self.incPC(2 - ((self.p & self.MS)>>5))

    @instruction(name="TXA", mode="imp", cycles=2)
    def inst_0x8a(self):
        if self.p & self.MS and self.isCLR(self.IRS):
            # A is 8 bit and X is 16 bit
            self.a = self.x & self.byteMask
        else:
            # A and X both 8 bit, or both 16 bit, or A is 16 and X is 8
            self.a = self.x

        if self.p & self.MS:
            self.FlagsNZ(self.a)
        else:
            self.FlagsNZWord(self.a)

    @instruction(name="PHB", mode="stk", cycles=3) # new to 65816
    def inst_0x8B(self):
        self.stPush(self.dbr)

    @instruction(name="STY", mode="abs", cycles=4)
    def inst_0x8c(self):
        self.opSTY(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="STA", mode="abs", cycles=4)
    def inst_0x8d(self):
        self.opSTA(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="STX", mode="abs", cycles=4)
    def inst_0x8e(self):
        self.opSTX(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="STA", mode="abl", cycles=5) # new to 65816
    def inst_0x8F(self):
        self.opSTA(self.AbsoluteLongAddr)
        self.incPC(3)

    @instruction(name="BCC", mode="pcr", cycles=2, extracycles=2)
    def inst_0x90(self):
        self.bCLR(self.CARRY)

    @instruction(name="STA", mode="diy", cycles=6)
    def inst_0x91(self):
        self.opSTA(self.DirectPageIndirectYAddr)
        self.incPC()

    @instruction(name="STA", mode="dpi", cycles=5)
    def inst_0x92(self):
        self.opSTA(self.DirectPageIndirectAddr)
        self.incPC()

    @instruction(name="STA", mode="siy", cycles=7) # new to 65816
    def inst_0x93(self):
        self.opSTA(self.StackRelIndirectYAddr)
        self.incPC()

    @instruction(name="STY", mode="dpx", cycles=4)
    def inst_0x94(self):
        self.opSTY(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="STA", mode="dpx", cycles=4)
    def inst_0x95(self):
        self.opSTA(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="STX", mode="dpy", cycles=4)
    def inst_0x96(self):
        self.opSTX(self.DirectPageYAddr)
        self.incPC()

    @instruction(name="STA", mode="dly", cycles=6) # new to 65816
    def inst_0x97(self):
        self.opSTA(self.DirectPageIndirectLongYAddr)
        self.incPC()

    @instruction(name="TYA", mode="imp", cycles=2)
    def inst_0x98(self):
        if self.p & self.MS and self.isCLR(self.IRS):
            # A is 8 bit and Y is 16 bit
            self.a = self.y & self.byteMask
        else:
            # A and Y both 8 bit, or both 16 bit, or A is 16 and Y is 8
            self.a = self.y

        if self.p & self.MS:
            self.FlagsNZ(self.a)
        else:
            self.FlagsNZWord(self.a)

    @instruction(name="STA", mode="aby", cycles=5)
    def inst_0x99(self):
        self.opSTA(self.AbsoluteYAddr)
        self.incPC(2)

    @instruction(name="TXS", mode="imp", cycles=2)
    def inst_0x9a(self):
        if self.mode:
            self.sp = self.x
        else:
            if self.p & self.IRS:
                # sp high byte is zero
                self.sp = self.x & self.byteMask
            else:
                self.sp = self.x

    @instruction(name="TXY", mode="imp", cycles=2) # new to 65816
    def inst_0x9b(self):
        self.y = self.x
        if self.p & self.IRS:
            self.FlagsNZ(self.y)
        else:
            self.FlagsNZWord(self.y)

    @instruction(name="STZ", mode="abs", cycles=4)
    def inst_0x9c(self):
        self.opSTZ(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="STA", mode="abx", cycles=5)
    def inst_0x9d(self):
        self.opSTA(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="STZ", mode="abx", cycles=5)
    def inst_0x9e(self):
        self.opSTZ(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="STA", mode="alx", cycles=5) # new to 65816
    def inst_0x9f(self):
        self.opSTA(self.AbsoluteLongXAddr)
        self.incPC(3)

    @instruction(name="LDY", mode="imm", cycles=2)
    def inst_0xa0(self):
        self.opLDY(self.ImmediateAddr)
        self.incPC(2 - ((self.p & self.IRS)>>4))

    @instruction(name="LDA", mode="dix", cycles=6)
    def inst_0xa1(self):
        self.opLDA(self.DirectPageIndirectXAddr)
        self.incPC()

    @instruction(name="LDX", mode="imm", cycles=2)
    def inst_0xa2(self):
        self.opLDX(self.ImmediateAddr)
        self.incPC(2 - ((self.p & self.IRS)>>4))

    @instruction(name="LDA", mode="str", cycles=4) # new to 65816
    def inst_0xa3(self):
        self.opLDA(self.StackRelAddr)
        self.incPC()

    @instruction(name="LDY", mode="dpg", cycles=3)
    def inst_0xa4(self):
        self.opLDY(self.DirectPageAddr)
        self.incPC()

    @instruction(name="LDA", mode="dpg", cycles=3)
    def inst_0xa5(self):
        self.opLDA(self.DirectPageAddr)
        self.incPC()

    @instruction(name="LDX", mode="dpg", cycles=3)
    def inst_0xa6(self):
        self.opLDX(self.DirectPageAddr)
        self.incPC()

    @instruction(name="LDA", mode="dil", cycles=6) # new to 65816
    def inst_0xa7(self):
        self.opLDA(self.DirectPageIndirectLongAddr)
        self.incPC()

    @instruction(name="TAY", mode="imp", cycles=2)
    def inst_0xa8(self):
        if self.p & self.MS and self.isCLR(self.IRS):
            # A is 8 bit and Y is 16 bit, hidden B is transfered as well
            self.y = (self.b << self.BYTE_WIDTH) + self.a
        elif self.isCLR(self.MS) and self.isSET(self.IRS):
            # A is 16 bit and Y is 8 bit
            self.y = self.a & self.byteMask
        else:
            # A and Y both 8 bit, or both 16 bit
            self.y = self.a

        if self.p & self.IRS:
            self.FlagsNZ(self.y)
        else:
            self.FlagsNZWord(self.y)

    @instruction(name="LDA", mode="imm", cycles=2)
    def inst_0xa9(self):
        self.opLDA(self.ImmediateAddr)
        self.incPC(2 - ((self.p & self.MS)>>5))

    @instruction(name="TAX", mode="imp", cycles=2)
    def inst_0xaa(self):
        if self.p & self.MS and self.isCLR(self.IRS):
            # A is 8 bit and X is 16 bit, hidden B is transfered as well
            self.x = (self.b << self.BYTE_WIDTH) + self.a
        elif self.isCLR(self.MS) and self.isSET(self.IRS):
            # A is 16 bit and X is 8 bit
            self.x = self.a & self.byteMask
        else:
            # A and X both 8 bit, or both 16 bit
            self.x = self.a

        if self.p & self.IRS:
            self.FlagsNZ(self.x)
        else:
            self.FlagsNZWord(self.x)

    @instruction(name="PLB", mode="stk", cycles=4) # new to 65816
    def inst_0xab(self):
        self.dbr = self.stPop()

    @instruction(name="LDY", mode="abs", cycles=4)
    def inst_0xac(self):
        self.opLDY(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="LDA", mode="abs", cycles=4)
    def inst_0xad(self):
        self.opLDA(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="LDX", mode="abs", cycles=4)
    def inst_0xae(self):
        self.opLDX(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="LDA", mode="abl", cycles=5) # new to 65816
    def inst_0xaf(self):
        self.opLDA(self.AbsoluteLongAddr)
        self.incPC(3)

    @instruction(name="BCS", mode="pcr", cycles=2, extracycles=2)
    def inst_0xb0(self):
        self.bSET(self.CARRY)

    @instruction(name="LDA", mode="diy", cycles=5, extracycles=1)
    def inst_0xb1(self):
        self.opLDA(self.DirectPageIndirectYAddr)
        self.incPC()

    @instruction(name="LDA", mode="dpi", cycles=5)
    def inst_0xb2(self):
        self.opLDA(self.DirectPageIndirectAddr)
        self.incPC()

    @instruction(name="LDA", mode="siy", cycles=7) # new to 65816
    def inst_0xb3(self):
        self.opLDA(self.StackRelIndirectYAddr)
        self.incPC()

    @instruction(name="LDY", mode="dpx", cycles=4)
    def inst_0xb4(self):
        self.opLDY(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="LDA", mode="dpx", cycles=4)
    def inst_0xb5(self):
        self.opLDA(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="LDX", mode="dpy", cycles=4)
    def inst_0xb6(self):
        self.opLDX(self.DirectPageYAddr)
        self.incPC()

    @instruction(name="LDA", mode="dly", cycles=6) # new to 65816
    def inst_0xb7(self):
        self.opLDA(self.DirectPageIndirectLongYAddr)
        self.incPC()

    @instruction(name="CLV", mode="imp", cycles=2)
    def inst_0xb8(self):
        self.pCLR(self.OVERFLOW)

    @instruction(name="LDA", mode="aby", cycles=4, extracycles=1)
    def inst_0xb9(self):
        self.opLDA(self.AbsoluteYAddr)
        self.incPC(2)

    @instruction(name="TSX", mode="imp", cycles=2)
    def inst_0xba(self):
        if self.p & self.IRS:
            self.x = self.sp & self.byteMask
            self.FlagsNZ(self.x)
        else:
            self.x = self.sp
            self.FlagsNZWord(self.x)

    @instruction(name="TYX", mode="imp", cycles=2) # new to 65816
    def inst_0xbb(self):
        self.x = self.y
        if self.p & self.IRS:
            self.FlagsNZ(self.x)
        else:
            self.FlagsNZWord(self.x)

    @instruction(name="LDY", mode="abx", cycles=4, extracycles=1)
    def inst_0xbc(self):
        self.opLDY(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="LDA", mode="abx", cycles=4, extracycles=1)
    def inst_0xbd(self):
        self.opLDA(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="LDX", mode="aby", cycles=4, extracycles=1)
    def inst_0xbe(self):
        self.opLDX(self.AbsoluteYAddr)
        self.incPC(2)

    @instruction(name="LDA", mode="alx", cycles=5) # new to 65816
    def inst_0xbf(self):
        self.opLDA(self.AbsoluteLongXAddr)
        self.incPC(3)

    @instruction(name="CPY", mode="imm", cycles=2)
    def inst_0xc0(self):
        self.opCMP(self.ImmediateAddr, self.y, self.IRS)
        self.incPC(2 - ((self.p & self.IRS)>>4))

    @instruction(name="CMP", mode="dix", cycles=6)
    def inst_0xc1(self):
        self.opCMP(self.DirectPageIndirectXAddr, self.a, self.MS)
        self.incPC()

    @instruction(name="REP", mode="imm", cycles=3) # new to 65816
    def inst_0xc2(self):
        operand = self.OperandByte()
        mask = self.CARRY
        while mask:
#            if mask & operand and not (self.mode and (mask & self.BREAK or mask & self.UNUSED)):
#                if mask == self.MS and self.isSET(self.MS):
#                    # A 8 => 16, set A = b a
#                    self.a = (self.b << self.BYTE_WIDTH) + self.a
#                    self.b = 0
#                self.pCLR(mask)

            # *** TODO: consider reworking SEP also to make conditionals clearer ***
            if mask & operand:
                if self.mode:
                    # can't change BREAK or UNUSED flags in emulation mode
                    if not (mask & self.BREAK or mask & self.UNUSED):
                        self.pCLR(mask)
                else:
                    if mask == self.MS and self.isSET(self.MS):
                        # A 8 => 16, set A = b a
                        self.a = (self.b << self.BYTE_WIDTH) + self.a
                        self.b = 0
                    self.pCLR(mask)

            mask = (mask << 1) & self.byteMask
        self.incPC()

    @instruction(name="CMP", mode="str", cycles=4) # new to 65816
    def inst_0xc3(self):
        self.opCMP(self.StackRelAddr, self.a, self.MS)
        self.incPC()

    @instruction(name="CPY", mode="dpg", cycles=3)
    def inst_0xc4(self):
        self.opCMP(self.DirectPageAddr, self.y, self.IRS)
        self.incPC()

    @instruction(name="CMP", mode="dpg", cycles=3)
    def inst_0xc5(self):
        self.opCMP(self.DirectPageAddr, self.a, self.MS)
        self.incPC()

    @instruction(name="DEC", mode="dpg", cycles=5)
    def inst_0xc6(self):
        self.opDECR(self.DirectPageAddr)
        self.incPC()

    @instruction(name="CMP", mode="dil", cycles=6) # new to 65816
    def inst_0xc7(self):
        self.opCMP(self.DirectPageIndirectLongAddr, self.a, self.MS)
        self.incPC()

    @instruction(name="INY", mode="imp", cycles=2)
    def inst_0xc8(self):
        self.y += 1
        if self.p & self.IRS:
            self.y &= self.byteMask
            self.FlagsNZ(self.y)
        else:
            self.y &= self.addrMask
            self.FlagsNZWord(self.y)

    @instruction(name="CMP", mode="imm", cycles=2)
    def inst_0xc9(self):
        self.opCMP(self.ImmediateAddr, self.a, self.MS)
        self.incPC(2 - ((self.p & self.MS)>>5))

    @instruction(name="DEX", mode="imp", cycles=2)
    def inst_0xca(self):
        self.x -= 1
        if self.p & self.IRS:
            self.x &= self.byteMask
            self.FlagsNZ(self.x)
        else:
            self.x &= self.addrMask
            self.FlagsNZWord(self.x)

    @instruction(name="WAI", mode='imp', cycles=3)
    def inst_0xcb(self):
        self.waiting = True

    @instruction(name="CPY", mode="abs", cycles=4)
    def inst_0xcc(self):
        self.opCMP(self.AbsoluteAddr, self.y, self.IRS)
        self.incPC(2)

    @instruction(name="CMP", mode="abs", cycles=4)
    def inst_0xcd(self):
        self.opCMP(self.AbsoluteAddr, self.a, self.MS)
        self.incPC(2)

    @instruction(name="DEC", mode="abs", cycles=3)
    def inst_0xce(self):
        self.opDECR(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="CMP", mode="abl", cycles=5) # new to 65816
    def inst_0xcf(self):
        self.opCMP(self.AbsoluteLongAddr, self.a, self.MS)
        self.incPC(3)

    @instruction(name="BNE", mode="pcr", cycles=2, extracycles=2)
    def inst_0xd0(self):
        self.bCLR(self.ZERO)

    @instruction(name="CMP", mode="diy", cycles=5, extracycles=1)
    def inst_0xd1(self):
        self.opCMP(self.DirectPageIndirectYAddr, self.a, self.MS)
        self.incPC()

    @instruction(name="CMP", mode='dpi', cycles=5)
    def inst_0xd2(self):
        self.opCMP(self.DirectPageIndirectAddr, self.a, self.MS)
        self.incPC()

    @instruction(name="CMP", mode="siy", cycles=7) # new to 65816
    def inst_0xd3(self):
        self.opCMP(self.StackRelIndirectYAddr, self.a, self.MS)
        self.incPC()

    @instruction(name="PEI", mode="ski", cycles=6) # new to 65816
    def inst_0xd4(self):
        addr = self.WordAt(self.dpr + self.OperandByte()) # in Bank 0
        self.stPushWord(addr)
        self.incPC()

    @instruction(name="CMP", mode="dpx", cycles=4)
    def inst_0xd5(self):
        self.opCMP(self.DirectPageXAddr, self.a, self.MS)
        self.incPC()

    @instruction(name="DEC", mode="dpx", cycles=6)
    def inst_0xd6(self):
        self.opDECR(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="CMP", mode="dly", cycles=6) # new to 65816
    def inst_0xd7(self):
        self.opCMP(self.DirectPageIndirectLongYAddr, self.a, self.MS)
        self.incPC()

    @instruction(name="CLD", mode="imp", cycles=2)
    def inst_0xd8(self):
        self.pCLR(self.DECIMAL)

    @instruction(name="CMP", mode="aby", cycles=4, extracycles=1)
    def inst_0xd9(self):
        self.opCMP(self.AbsoluteYAddr, self.a, self.MS)
        self.incPC(2)

    @instruction(name="PHX", mode="stk", cycles=3)
    def inst_0xda(self):
        if self.p & self.IRS:
            self.stPush(self.x)
        else:
            self.stPushWord(self.x)

    @instruction(name="STP", mode="imp", cycles=3) # new to 65816
    def inst_0xdb(self):
        # *** TODO: need to implement stop the processor ***
        # *** and wait for reset pin to be pulled low    ***
        # *** for now just reset ***
        self.reset()

    @instruction(name="JML", mode="ail", cycles=6)  # new to 65816
    def inst_0xdc(self):
        addr = self.OperandWord()
#        self.pbr = self.ByteAt(self.pc + 2)
#        self.pc = self.WordAt(self.OperandWord())
        self.pbr = self.ByteAt(addr + 2)
        self.pc = self.WordAt(addr)

    @instruction(name="CMP", mode="abx", cycles=4, extracycles=1)
    def inst_0xdd(self):
        self.opCMP(self.AbsoluteXAddr, self.a, self.MS)
        self.incPC(2)

    @instruction(name="DEC", mode="abx", cycles=7)
    def inst_0xde(self):
        self.opDECR(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="CMP", mode="alx", cycles=5) # new to 65816
    def inst_0xdf(self):
        self.opCMP(self.AbsoluteLongXAddr, self.a, self.MS)
        self.incPC(3)

    @instruction(name="CPX", mode="imm", cycles=2)
    def inst_0xe0(self):
        self.opCMP(self.ImmediateAddr, self.x, self.IRS)
        self.incPC(2 - ((self.p & self.IRS)>>4))

    @instruction(name="SBC", mode="dix", cycles=6)
    def inst_0xe1(self):
        self.opSBC(self.DirectPageIndirectXAddr)
        self.incPC()

    @instruction(name="SEP", mode="imm", cycles=3) # new to 65816
    def inst_0xe2(self):
        operand = self.OperandByte()
        mask = self.CARRY
        while mask:
            # can't change BREAK or UNUSED flags in emulation mode
            if mask & operand and not (self.mode and (mask & self.BREAK or mask & self.UNUSED)):
                if mask == self.MS and self.isCLR(self.MS):
                    # A 16 => 8, save B, mask A high byte
                    self.b = (self.a >> self.BYTE_WIDTH) & self.byteMask
                    self.a = self.a & self.byteMask
                elif mask == self.IRS and self.isCLR(self.IRS):
                    # X,Y 16 => 8, set high byte to zero
                    self.x = self.x & self.byteMask
                    self.y = self.y & self.byteMask
                self.pSET(mask)
            mask = (mask << 1) & self.byteMask
        self.incPC()

    @instruction(name="SBC", mode="str", cycles=4) # new to 65816
    def inst_0xe3(self):
        self.opSBC(self.StackRelAddr)
        self.incPC()

    @instruction(name="CPX", mode="dpg", cycles=3)
    def inst_0xe4(self):
        self.opCMP(self.DirectPageAddr, self.x, self.IRS)
        self.incPC()

    @instruction(name="SBC", mode="dpg", cycles=3)
    def inst_0xe5(self):
        self.opSBC(self.DirectPageAddr)
        self.incPC()

    @instruction(name="INC", mode="dpg", cycles=5)
    def inst_0xe6(self):
        self.opINCR(self.DirectPageAddr)
        self.incPC()

    @instruction(name="SBC", mode="dil", cycles=6) # new to 65816
    def inst_0xe7(self):
        self.opSBC(self.DirectPageIndirectLongAddr)
        self.incPC()

    @instruction(name="INX", mode="imp", cycles=2)
    def inst_0xe8(self):
        self.x += 1
        if self.p & self.IRS:
            self.x &= self.byteMask
            self.FlagsNZ(self.x)
        else:
            self.x &= self.addrMask
            self.FlagsNZWord(self.x)

    @instruction(name="SBC", mode="imm", cycles=2)
    def inst_0xe9(self):
        self.opSBC(self.ImmediateAddr)
        self.incPC(2 - ((self.p & self.MS)>>5))

    @instruction(name="NOP", mode="imp", cycles=2)
    def inst_0xea(self):
        pass

    @instruction(name="XBA", mode="imp", cycles=3) # new to 65816
    def inst_0xeb(self):
        a = self.a & self.byteMask

        if self.p & self.MS: # 8 bit
            b = self.b
            self.a = b
            self.b = a
        else: # 16 bits
            b = (self.a >> self.BYTE_WIDTH) & self.byteMask
            self.a = (a << self.BYTE_WIDTH) + b

        # *** TODO: check if B is ever relevant w/ 16-bit A.
        # Basically, do I need to maintain a hidden B even when I have
        # it as the high byte in A. ***

        self.FlagsNZ(b)

    @instruction(name="CPX", mode="abs", cycles=4)
    def inst_0xec(self):
        self.opCMP(self.AbsoluteAddr, self.x, self.IRS)
        self.incPC(2)

    @instruction(name="SBC", mode="abs", cycles=4)
    def inst_0xed(self):
        self.opSBC(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="INC", mode="abs", cycles=6)
    def inst_0xee(self):
        self.opINCR(self.AbsoluteAddr)
        self.incPC(2)

    @instruction(name="SBC", mode="abl", cycles=5) # new to 65816
    def inst_0xef(self):
        self.opSBC(self.AbsoluteLongAddr)
        self.incPC(3)

    @instruction(name="BEQ", mode="pcr", cycles=2, extracycles=2)
    def inst_0xf0(self):
        self.bSET(self.ZERO)

    @instruction(name="SBC", mode="diy", cycles=5, extracycles=1)
    def inst_0xf1(self):
        self.opSBC(self.DirectPageIndirectYAddr)
        self.incPC()

    @instruction(name="SBC", mode="dpi", cycles=5)
    def inst_0xf2(self):
        self.opSBC(self.DirectPageIndirectAddr)
        self.incPC()

    @instruction(name="SBC", mode="siy", cycles=7) # new to 65816
    def inst_0xf3(self):
        self.opSBC(self.StackRelIndirectYAddr)
        self.incPC()

    @instruction(name="PEA", mode="ska", cycles=5) # new to 65816
    def inst_0xf4(self):
        self.stPushWord(self.OperandWord())
        self.incPC(2)

    @instruction(name="SBC", mode="dpx", cycles=4)
    def inst_0xf5(self):
        self.opSBC(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="INC", mode="dpx", cycles=6)
    def inst_0xf6(self):
        self.opINCR(self.DirectPageXAddr)
        self.incPC()

    @instruction(name="SBC", mode="dly", cycles=6) # new to 65816
    def inst_0xf7(self):
        self.opSBC(self.DirectPageIndirectLongYAddr)
        self.incPC()

    @instruction(name="SED", mode="imp", cycles=2)
    def inst_0xf8(self):
        self.pSET(self.DECIMAL)

    @instruction(name="SBC", mode="aby", cycles=4, extracycles=1)
    def inst_0xf9(self):
        self.opSBC(self.AbsoluteYAddr)
        self.incPC(2)

    @instruction(name="PLX", mode="stk", cycles=4)
    def inst_0xfa(self):
        if self.p & self.IRS:
            self.x = self.stPop()
            self.FlagsNZ(self.x)
        else:
            self.x = self.stPopWord()
            self.FlagsNZWord(self.x)

    @instruction(name="XCE", mode="imp", cycles=2) # new to 65816
    def inst_0xfb(self):
        # *** TODO: 65816 Programming Manual, pg 423,
        # describes these action as only happening when actually switching
        # modes.  Verify that M and X don't change if XCE is called when
        # already in the selected mode (i.e., XCE can't be used as a fast
        # way to change to 8 bit registers). ***
        if self.mode and self.isCLR(self.CARRY): # emul => native
            self.pSET(self.MS)
            self.pSET(self.IRS)
            self.pSET(self.CARRY)
            self.mode = 0
            self.sp = 0x100 + self.sp
        elif not self.mode and self.isSET(self.CARRY): # native => emul
            self.pSET(self.BREAK)
            self.pSET(self.UNUSED)
            self.pCLR(self.CARRY)
            self.b = (self.a >> self.BYTE_WIDTH) & self.byteMask
            self.a = self.a & self.byteMask
            self.x = self.x & self.byteMask
            self.y = self.y & self.byteMask
            self.sp = (self.sp & self.byteMask)
            self.mode = 1

    @instruction(name="JSR", mode="aix", cycles=8) # new to 65816
    def inst_0xfc(self):
        self.stPushWord((self.pc + 1) & self.addrMask)
        self.pc = self.WordAt(self.AbsoluteIndirectXAddr())

    @instruction(name="SBC", mode="abx", cycles=4, extracycles=1)
    def inst_0xfd(self):
        self.opSBC(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="INC", mode="abx", cycles=7)
    def inst_0xfe(self):
        self.opINCR(self.AbsoluteXAddr)
        self.incPC(2)

    @instruction(name="SBC", mode="alx", cycles=5) # new to 65816
    def inst_0xff(self):
        self.opSBC(self.AbsoluteLongXAddr)
        self.incPC(3)

