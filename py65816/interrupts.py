from py65816.devices.via65c22 import VIA
from py65816.devices.acia65c51 import ACIA

class Interrupts:
    def __init__(self, mon, mpu):

        self.mpu = mpu
        self.mon = mon
        self.blockFile = None
        self.VIA = None
        self.ACIA = None

    def addVIA(self, addr):
        self.VIA = VIA(addr, self.mpu)

    def addACIA(self, addr, filename):
        self.ACIA = ACIA(addr, filename, self.mpu, self.mon)
