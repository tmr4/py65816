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

