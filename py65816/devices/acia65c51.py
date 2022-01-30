import sys

class ACIA():
    # acia status register flags
    INTERRUPT = 128 # interrupt has occured, read status register to clear
    DSREADY = 64
    DCDETECT = 32
    TDREMPTY = 16
    RDRFULL = 8 # receiver data register full
    OVERRUN = 4
    FRAMING = 2
    PARITY = 1

    def __init__(self, start_addr, filename, mpu, monitor):

        self.name = 'ACIA'
        self.mpu = mpu
        self.mon = monitor        
        self.RDATAR = start_addr
        self.TDATAR = start_addr
        self.STATUSR = start_addr + 1
        self.COMDR = start_addr + 2
        self.escape = False
        self.block = False
        self.bbuffer = 0
        self.bcount = 1024
        self.block_file = filename

        # init
        self.reset()

        self.install_interrupts()

    def install_interrupts(self):
        def dataT_callback(address, value):
            mpu = self.mpu
            try:
                if self.escape:
                    if value == 0x42:
                        if self.block_file is not None:
                            self.block = True
                    elif self.block:
                        fo = open(self.block_file, "rb")
                        fo.seek(value*1024,0)
                        self.bbuffer = fo.read(1024)
                        fo.close()

                        mpu = self.mpu
                        self.bcount = 0
                        while self.bcount < 1024:
                            mpu.IRQ_pin = 0
                            mpu.memory[self.STATUSR] |= 0x88 # set Receiver Data Register Full flag (bit 3) status register
                            count = 0
                            while count < 50: # process interrupt and resulting character (*** TODO: this should be < 50 steps, could tighten up to speed Forth load ***)
                                mpu.step()
                                count += 1

                        self.block = False
                        self.escape = False
                    else:
                        sys.stdout.write(chr(0x1b))
                        sys.stdout.write(chr(value))
                        self.escape = False
                else:
                    if value == 0x1b:
                        self.escape = True
                    else:
                        sys.stdout.write(chr(value))
                        if value == 0x0d:
                            sys.stdout.write(chr(0x0a))

            except UnicodeEncodeError: # Python 3
                sys.stdout.write("?")
            sys.stdout.flush()

        def dataR_callback(address):
            if self.bcount >= 1024:
                return 0
            else:
                byte = self.bbuffer[self.bcount]
                self.bcount += 1
                self.mpu.memory[self.STATUSR] &= 0x77 # clear Receiver Data Register Full flag (bit 3) status register
                return byte

        self.mpu.memory.subscribe_to_write([self.TDATAR], dataT_callback)
        self.mpu.memory.subscribe_to_read([self.RDATAR], dataR_callback)

    def reset(self):
        self.mpu.memory[self.STATUSR] = 0
