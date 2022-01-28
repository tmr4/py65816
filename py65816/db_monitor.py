"""py65816mon -- interact with a simulated 65816-based system

Usage: %s [options]

Options:
-h, --help             : Show this message
-d, --debug            : Open debug window
-m, --mpu <device>     : Choose which MPU device (default is 6502)
-l, --load <file>      : Load a file at address 0
-r, --rom <file>       : Load a rom at the top of address space and reset into it
-g, --goto <address>   : Perform a goto command after loading any files
-i, --input <address>  : define location of getc (default $f004)
-o, --output <address> : define location of putc (default $f001)
"""

import getopt
import sys
import time

from py65.monitor import Monitor
from py65.assembler import Assembler
from py65.utils.addressing import AddressParser
from py65.utils import console
from py65.utils.conversions import itoa
from py65.memory import ObservableMemory

from py65816.devices.mpu65c816 import MPU as CMOS65C816
from py65816.db_server import db_server as server
from py65816.db_disassembler import dbDisassembler as Disassembler

class dbMonitor(Monitor):

    Monitor.Microprocessors["65C816"] = CMOS65C816

#    def __init__(self, argv=['db_monitor.py', '-m', '65c816', '-r', 'forth.bin', '-i', '7fc0', '-o', '7fe0', '-d'],
#    def __init__(self, argv=['db_monitor.py', '-m', '65c816', '-r', 'forth.bin', '-i', '7fc0', '-o', '7fe0'],
#    def __init__(self, argv=['db_monitor.py', '-h'],
#                       stdin=None, stdout=None,
#                       mpu_type=CMOS65C816, memory=None,
#                       putc_addr=0xfff1, getc_addr=0xfff0):
    def __init__(self, argv=None, stdin=None, stdout=None,
                       mpu_type=CMOS65C816, memory=None,
                       putc_addr=0xF001, getc_addr=0xF004):

        self.dbWin = False

        # check is the debug window is requested
        try:
            if argv is None:
                argv = sys.argv

            shortopts = 'hdi:o:m:l:r:g:'
            longopts = ['help', 'debug', 'mpu=', 'input=', 'output=', 'load=', 'rom=', 'goto=']
            options, args = getopt.getopt(argv[1:], shortopts, longopts)

            for opt, value in options:
                if opt in ('-d', '--debug'):
                    self.dbWin = True

                if opt in ("-h", "--help"):
                    self._usage()
                    self._exit(0)

        except:
            raise

        if self.dbWin:
            argv.pop()

        super().__init__(argv, stdin, stdout, mpu_type, memory, putc_addr, getc_addr)

        self._shortcuts['d'] = 'debug'

    def do_debug(self, args):
        if not self.dbWin:
            self.s = server(self, self._mpu, True)
            self.dbWin = True
        else:
            self.s.install_db(True)


    def help_debug(self):
        self._output("Open debug window.")

    def do_version(self, args):
        self._output("\n65816 Debug Monitor")

    def _reset(self, mpu_type, getc_addr=0xF004, putc_addr=0xF001):
        self._mpu = mpu_type(memory=self.memory)
        self.addrWidth = self._mpu.ADDR_WIDTH
        self.byteWidth = self._mpu.BYTE_WIDTH
        self.addrFmt = self._mpu.ADDR_FORMAT
        self.byteFmt = self._mpu.BYTE_FORMAT
        self.addrMask = self._mpu.addrMask
        self.byteMask = self._mpu.byteMask
        if getc_addr and putc_addr:
            self._install_mpu_observers(getc_addr, putc_addr)
        self._address_parser = AddressParser()
        self._disassembler = Disassembler(self._mpu, self._address_parser)
        self._assembler = Assembler(self._mpu, self._address_parser)

        if self.dbWin:
            self.s = server(self, self._mpu, self.dbWin)

    def _run(self, stopcodes):
        if self.dbWin:
            try:
                self.s.do_db(stopcodes, self._breakpoints)
            except KeyboardInterrupt:
                print('Breaking to monitor ...')
            except:
                print('Uncaught error, breaking to monitor ...')
        else:
            super()._run(stopcodes)

    def _usage(self):
        usage = __doc__ % sys.argv[0]
        print(usage)

    def _install_mpu_observers(self, getc_addr, putc_addr):
        def putc(address, value):
            try:
                self.stdout.write(chr(value))
            except UnicodeEncodeError: # Python 3
                self.stdout.write("?")
            self.stdout.flush()

        def getc(address):
            char = console.getch_noblock(self.stdin)
            time.sleep(.1) # reduce cpu usage (~55% to ~2%) in Forth interpret loop (comment out for full speed ops)
            if char:
                byte = ord(char)
            else:
                byte = 0
            return byte

        m = ObservableMemory(subject=self.memory, addrWidth=self.addrWidth)
        m.subscribe_to_write([self.putc_addr], putc)
        m.subscribe_to_read([self.getc_addr], getc)

        self._mpu.memory = m

    def _format_disassembly(self, address, length, disasm):
        cur_address = address
        max_address = (2 ** self._mpu.ADDR_WIDTH) - 1

        bytes_remaining = length
        dump = ''

        while bytes_remaining:
            if cur_address > max_address:
                cur_address = 0
            dump += self.byteFmt % self._mpu.memory[cur_address] + " "
            cur_address += 1
            bytes_remaining -= 1

        fieldwidth = 1 + int(1 + self.byteWidth / 4) * 3
        fieldfmt = "%%-%ds" % fieldwidth

        if self._mpu.name == '65C816':
            pbrfmt = "%02x"
            return "$" + pbrfmt % self._mpu.pbr + ":" + self.addrFmt % address + "  " + fieldfmt % dump + disasm
        else:
            return "$" + self.addrFmt % address + "  " + fieldfmt % dump + disasm

def main(args=None):
    c = dbMonitor()

    try:
        c.onecmd('version')
        c.cmdloop()
    except KeyboardInterrupt:
        c._output('')
        console.restore_mode()

if __name__ == "__main__":
    main()
