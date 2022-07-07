import sys

from py65816.utils import db_console

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

    def __init__(self, start_addr, filename, mpu, monitor, interrupt):

        self.name = 'ACIA'
        self.mpu = mpu
        self.mon = monitor
        self.int = interrupt
        self.RDATAR = start_addr
        self.TDATAR = start_addr
        self.STATUSR = start_addr + 1
        self.COMDR = start_addr + 2
        self.escape = False
        self.block = False
        self.bbuffer = 0
        self.bcount = 1024
        self.block_file = filename
        self.status_reg = 0
        self.control_reg = 0
        self.command_reg = 0
        self.enabled = False
        self.oldenabled = False

        # init
        self.reset()

        self.install_interrupts()

    def install_interrupts(self):

        def dataT_callback(address, value):
            try:
                if self.escape:
                    if value == 0x42:
                        # signal block load if block file is available
                        if self.block_file is not None:
                            self.block = True
                    elif self.block:
                        # load block # indicated by value
                        fo = open(self.block_file, "rb")
                        fo.seek(value*1024,0)
                        self.bbuffer = fo.read(1024)
                        fo.close()

                        self.dataT_enable()

                        self.block = False
                        self.escape = False
                    else:
                        sys.stdout.write(chr(0x1b))
                        sys.stdout.write(chr(value))
                        self.escape = False
                else:
                    if value == 0x1b:
                        # signal that we're in an escape sequence
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
                self.status_reg &= 0x77 # clear Receiver Data Register Full flag (bit 3) status register
                return byte

        def aciaReset_callback(address, value):
            self.reset()

        def aciaStatus_callback(address):
            tmp = self.status_reg
            self.status_reg &= 0x7f # clear interrupt flag (bit 7) in status register
            return tmp

        self.mpu.memory.subscribe_to_write([self.TDATAR], dataT_callback)
        self.mpu.memory.subscribe_to_read([self.RDATAR], dataR_callback)

        self.mpu.memory.subscribe_to_write([self.STATUSR], aciaReset_callback)
        self.mpu.memory.subscribe_to_read([self.STATUSR], aciaStatus_callback)

    def reset(self):
        self.status_reg = 0
        self.control_reg = 0
        # self.command_reg = 0

    def dataT_thread(self):
        mpu = self.mpu
        if self.bcount < 1024:
            if (mpu.IRQ_pin == 1) and (mpu.p & mpu.INTERRUPT == 0):
                mpu.IRQ_pin = 0
                self.status_reg |= 0x88 # set Receiver Data Register Full flag (bit 3) status register
        else:
            self.enabled = False
            self.int.enabled = self.oldenabled

    def dataT_enable(self):
        self.enabled = True
        self.oldenabled = self.int.enabled
        self.int.enabled = True
        self.bcount = 0

