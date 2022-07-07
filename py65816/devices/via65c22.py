import sys

from py65.utils import console
from py65816.utils import db_console

class VIA():

    SR = 4
    SET_CLEAR = 128

    def __init__(self, start_addr, mpu, interrupt):
        self.mpu = mpu
        self.int = interrupt

        self.VIA_SR  = start_addr + 0x0a   # shift register
        self.VIA_IFR = start_addr + 0x0d   # interrupt flags register
        self.VIA_IER = start_addr + 0x0e   # interrupt enable register
        self.escape = False

        self.enabled = False
        self.oldenabled = False

        self.name = 'VIA'

        # init
        self.reset()

        self.install_interrupts()

    def install_interrupts(self):
        def getc(address):
            char = console.getch_noblock(sys.stdin)
            if char:
                byte = ord(char)
                if self.escape:
                    self.escape = False
                    if byte == 0x51 or byte == 0x71:
                        self.mpu.pc = 65527 # set pc to a break instruction which drops us to the monitor program
                        byte = 0
                else:
                    if byte == 0x1b:
                        self.escape = True
                        byte = 0
                    else:
                        self.mpu.memory[self.VIA_IFR] &= 0xfb
            else:
                byte = 0

            return byte

        self.mpu.memory.subscribe_to_write([self.VIA_IER], self.SR_enable)
        self.mpu.memory.subscribe_to_read([self.VIA_SR], getc)

    def reset(self):
        self.mpu.memory[self.VIA_IER] = 0
        self.mpu.memory[self.VIA_IFR] = 0

    #def irq(self):
        #return (IFR6 and IER6) or (IFR5 and IER5) or (IFR4 and IER4) or (IFR3 and IER3) or (IFR2 and IER2) or (IFR1 and IER1) or (IFR0 and IER0)
        #return (self.mpu.memory[self.VIA_IFR] and self.SR) and ((self.mpu.memory[self.VIA_IER] and self.SR))

    def SR_enable(self, address, value):
        if value & self.SET_CLEAR:
            # enable interrupts
            if value & self.SR:
                self.enabled = True
                self.oldenabled = self.int.enabled
                self.int.enabled = True
        else:
            # disable interrupts
            self.enabled = False
            self.int.enabled = self.oldenabled

    def SR_thread(self):
        mpu = self.mpu
        if (mpu.IRQ_pin == 1) and (mpu.p & mpu.INTERRUPT == 0):
            if db_console.kbhit():
                mpu.memory[self.VIA_IFR] |= 0x04
                mpu.IRQ_pin = 0

