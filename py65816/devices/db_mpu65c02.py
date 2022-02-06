from py65.devices import mpu65c02

class MPU(mpu65c02.MPU):
    def __init__(self, *args, **kwargs):
        mpu65c02.MPU.__init__(self, *args, **kwargs)
        self.name = 'db65C02'
        self.waiting = False
        self.IRQ_pin = 1

    def step(self):
        if self.waiting:
            self.processorCycles += 1
        else:
            if (self.IRQ_pin == 0) and (self.p & self.INTERRUPT == 0):
                self.irq()
                self.IRQ_pin = 1

            mpu65c02.MPU.step(self)
        return self

    def irq(self):
        # triggers an IRQ
        if self.p & self.INTERRUPT:
            return

        self.p &= ~self.BREAK
        self.p | self.UNUSED

        self.stPushWord(self.pc)
        self.stPush(self.p)

        self.p |= self.INTERRUPT
        self.pc = self.WordAt(self.IRQ)
        self.processorCycles += 7

    #*****************************************************************************
    # Operations

    def opADC(self, x):
        data = self.ByteAt(x())

        if self.p & self.DECIMAL:
            # Includes proposed fix from:
            # https://github.com/mnaberez/py65/pull/55/commits/666cd9cd99484f769b563218214433d37faa1d87
            # as discussed at: https://github.com/mnaberez/py65/issues/33
            # 
            # This now passed 8-bit BCD tests from: 
            # http://6502.org/tutorials/decimal_mode.html#B
            # that I've modeled at: C:\Users\tmrob\Documents\Projects\65C816\Assembler\decimal
            #
            #       C:\Users\tmrob\Documents\Projects\65C816\Assembler\decimal>bcd_db65c02
            #       
            #       C:\Users\tmrob\Documents\Projects\65C816\Assembler\decimal>py65816mon -m db65c02 -r bcd_65c02.bin -i fff0 -o fff1
            #       Wrote +65536 bytes from $0000 to $ffff
            #       -------------------------------------
            #       65816 BCD Tests:
            #       -------------------------------------
            #       BCD,8
            #       Mode     | Test | NV-BDIZC | Result |
            #       -------------------------------------
            #       Emulation  ADC    01-10011   PASS
            #       Emulation  SBC    00-10011   PASS
            #       

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
#            aluresult = (nibble1 << 4) + nibble0

            # the final A contents will be decimally adjusted
            nibble0 = (nibble0 + adjust0) & 0xf
            nibble1 = (nibble1 + adjust1) & 0xf

            # Update result for use in setting flags below
            aluresult = (nibble1 << 4) + nibble0

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
            if (~(self.a ^ data) & (self.a ^ result)) & self.NEGATIVE:
                self.p |= self.OVERFLOW
            data = result
            if data > self.byteMask:
                self.p |= self.CARRY
                data &= self.byteMask
            if data == 0:
                self.p |= self.ZERO
            else:
                self.p |= data & self.NEGATIVE
            self.a = data

    def opSBC(self, x):
        data = self.ByteAt(x())

        if self.p & self.DECIMAL:
            # Includes proposed fix from:
            # https://github.com/mnaberez/py65/pull/55/commits/666cd9cd99484f769b563218214433d37faa1d87
            # as discussed at: https://github.com/mnaberez/py65/issues/33
            # 
            # This now passed 8-bit BCD tests from: 
            # http://6502.org/tutorials/decimal_mode.html#B
            #
            #       C:\Users\tmrob\Documents\Projects\65C816\Assembler\decimal>bcd_db65c02
            #       
            #       C:\Users\tmrob\Documents\Projects\65C816\Assembler\decimal>py65816mon -m db65c02 -r bcd_65c02.bin -i fff0 -o fff1
            #       Wrote +65536 bytes from $0000 to $ffff
            #       -------------------------------------
            #       65816 BCD Tests:
            #       -------------------------------------
            #       BCD,8
            #       Mode     | Test | NV-BDIZC | Result |
            #       -------------------------------------
            #       Emulation  ADC    01-10011   PASS
            #       Emulation  SBC    00-10011   PASS
            #       

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

            # Update result for use in setting flags below
            aluresult = (nibble1 << 4) + nibble0

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
            result = self.a + (~data & self.byteMask) + (self.p & self.CARRY)
            self.p &= ~(self.CARRY | self.ZERO | self.OVERFLOW | self.NEGATIVE)
            if ((self.a ^ data) & (self.a ^ result)) & self.NEGATIVE:
                self.p |= self.OVERFLOW
            data = result & self.byteMask
            if data == 0:
                self.p |= self.ZERO
            if result > self.byteMask:
                self.p |= self.CARRY
            self.p |= data & self.NEGATIVE
            self.a = data

