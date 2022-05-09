import sys
import time
import threading

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
        self.status_reg = 0
        self.control_reg = 0
        self.command_reg = 0

        # init
        self.reset()

        self.install_interrupts()

    def install_interrupts(self):
        def dataT_enable(address, value):
            t = threading.Thread(target=dataT_thread, daemon = True)
            t.start()

        def dataT_thread():
            mpu = self.mpu
            self.bcount = 0
            count = 0

            # request an interrupt to process each byte in block
            while count < 1024:
                # Given the serial nature of the block transfer, we need to ensure that the previous
                # interrupt has been processed before requesting another.  We can do this by using an 
                # appropirately timed delay or setting/checking a flag to indicate the interrupt service
                # routine has completed.

                # Using a sleep timer for the delay isn't desirable because the timing isn't guaranteed.
                # However, interestingly, they seem to allow a faster startup than using a status flag.
                # Using a timer instead of the status flag check, here and for the VIA,
                # actually speeds startup by about a half minute.
#                time.sleep(.005) # this delay works w/ startup taking about 2.5 minutes, shorter
                                  # delays don't increase startup speed materially

                # Alternatively we can check the interrupt status flag assuming it remains set until the
                # interrupt service routine has completed, thus nested interrupts aren't possible.
                # They likely aren't possible with the time delay above either but may be possible
                # with a longer delay.
                # This works well with VSCode debug, unclear if the sleep delay works with debug
                # This works with a startup time of about 3 minutes
                if (mpu.IRQ_pin == 1) and (mpu.p & mpu.INTERRUPT == 0):
                    mpu.IRQ_pin = 0
#                    mpu.memory[self.STATUSR] |= 0x88 # set Receiver Data Register Full flag (bit 3) status register
                    self.status_reg |= 0x88 # set Receiver Data Register Full flag (bit 3) status register

                    count += 1
                else:
                    time.sleep(0.001) # don't notice much change in startup time with or without this

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

                        # callbacks occur within a step and before pc has been fully incremented
                        # IRQs finish the current instruction before jumping to the servicing
                        # routine, thus we can't call step again from here to run through the routine
                        dataT_enable(address, value)

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
#                self.mpu.memory[self.STATUSR] &= 0x77 # clear Receiver Data Register Full flag (bit 3) status register
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
