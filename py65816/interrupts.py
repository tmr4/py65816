from py65816.devices.via65c22 import VIA
from py65816.devices.acia65c51 import ACIA

class Interrupts:
    def __init__(self, mon, mpu):

        self.mpu = mpu
        self.mon = mon
        self.blockFile = None
        self.VIA = None
        self.ACIA = None
        self.enabled = False

    def addVIA(self, addr):
        self.VIA = VIA(addr, self.mpu, self)

    def addACIA(self, addr, filename):
        self.ACIA = ACIA(addr, filename, self.mpu, self.mon, self)

    # poll devices and trip an interrupt if appropriate
    def trip(self):
        # Must have sufficient delay to allow interrupts and input
        # to be processed.  Threading and cycle counts proved
        # ineffective for this.  Threading took about 2.5 minutes
        # to start up and had very slow pasted input because threads
        # don't run concurrently in CPython and yielding with sleep
        # wasn't fine tuned enough.  Cycle counts worked well for 
        # startup but not for pastes as the time to processing input 
        # is variable and the circular input before is easily overflown.
        # Using the processor wait state is a good trade off.  It
        # gives a reasonable pasted input experience and only slightly
        # delays startup.  Note using the waiting state as a delay isn't
        # the fasted method for responding to input (I believe it doesn't
        # take advantage of the internal buffers) but it is reasonably
        # efficient. Start up with a tuned cycle count delay was about
        # 12 seconds.  It's about 17 seconds using waiting.  The difference
        # is processing the WAI instructions which are forced with this method
        # but never needed using a cycle count delay because at startup
        # the input is already buffered (i.e, available without waiting). 
        # Cycle count delays also affected each interrupt, that is, the
        # VIA delay would affect the ACIA delay, even though keyboard
        # input isn't expected during start up.
        if self.mpu.waiting:

            if self.ACIA.enabled:
                self.ACIA.dataT_thread()

            if self.VIA.enabled and not self.ACIA.enabled:
                self.VIA.SR_thread()            