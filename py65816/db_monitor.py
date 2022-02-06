"""py65816mon -- interact with a simulated 65816-based system

Usage: %s [options]

Options:
-h, --help                        : Show this message
-m, --mpu <device>                : Choose which MPU device (default is 65816)
-l, --load <file>                 : Load a file at address 0
-r, --rom <file>                  : Load a rom at the top of address space and reset into it
-g, --goto <address>              : Perform a goto command after loading any files
-i, --input <address>             : define location of getc (default $f004)
-o, --output <address>            : define location of putc (default $f001)
-w, --debug                       : Open debug window
-v, --via <address>               : Add a VIA at address
-a, --acia "<address> <filename>" : Add an ACIA at address with filename for block access
"""

import cmd
import getopt
import re
import shlex
import sys
import time

from py65.monitor import Monitor
from py65.utils.addressing import AddressParser
from py65.utils import console
from py65.utils.conversions import itoa
from py65.memory import ObservableMemory

from py65816.devices.mpu65c816 import MPU as CMOS65C816
from py65816.devices.db_mpu65c02 import MPU as DB65C816
from py65816.db_server import db_server as server
from py65816.db_disassembler import dbDisassembler as Disassembler
from py65816.db_assembler import dbAssembler as Assembler
from py65816.interrupts import Interrupts

class dbMonitor(Monitor):

    Monitor.Microprocessors["65C816"] = CMOS65C816
    Monitor.Microprocessors["DB65C02"] = DB65C816

    def __init__(self, argv=None, stdin=None, stdout=None,
                       mpu_type=CMOS65C816, memory=None,
                       putc_addr=0xF001, getc_addr=0xF004):
        self.mpu_type = mpu_type
        self.memory = memory
        self.putc_addr = putc_addr
        self.getc_addr = getc_addr
        self._breakpoints = []
        self._width = 72
        self.prompt = "."
        self._add_shortcuts()
        self._shortcuts['w'] = 'debug'

        self.dbWin = None
        self.dbInt = None
        
        cmd.Cmd.__init__(self, stdin=stdin, stdout=stdout)

        # Check for any exceptions thrown during __init__ while
        # processing the arguments.
        try:

            if argv is None:
                argv = sys.argv
                # *** allow tests with nose2 --with-coverage --coverage-report html ***
                if '--with-coverage' in argv:
                    argv.remove("--with-coverage")
                if '--coverage-report' in argv:
                    argv.remove("--coverage-report")
            load, rom, goto, win, via, acia = self._parse_args(argv)

            self._reset(self.mpu_type, self.getc_addr, self.putc_addr)

            if via is not None:
                self.do_via(via)

            if acia is not None:
                self.do_acia(acia)

            if win is not None:
                self.do_debug(None)

            if load is not None:
                self.do_load("%r" % load)

            if goto is not None:
                self.do_goto(goto)

            if rom is not None:
                # load a ROM and run from the reset vector
                self.do_load("%r top" % rom)
                physMask = self._mpu.memory.physMask
                reset = self._mpu.RESET & physMask
                dest = self._mpu.memory[reset] + \
                    (self._mpu.memory[reset + 1] << self.byteWidth)
                self.do_goto("$%x" % dest)
        except:
            raise

    def _parse_args(self, argv):
        try:
            shortopts = 'hwv:a:i:o:m:l:r:g:'
            longopts = ['help', 'debug', 'via=', 'acia=', 'mpu=', 'input=', 'output=', 'load=', 'rom=', 'goto=']
            options, args = getopt.getopt(argv[1:], shortopts, longopts)
        except getopt.GetoptError as exc:
            self._output(exc.args[0])
            self._usage()
            self._exit(1)

        load, rom, goto, win, via, acia = None, None, None, None, None, None

        for opt, value in options:
            if opt in ('-i', '--input'):
                self.getc_addr = int(value, 16)

            if opt in ('-o', '--output'):
                self.putc_addr = int(value, 16)

            if opt in ('-m', '--mpu'):
                mpu_type = self._get_mpu(value)
                if mpu_type is None:
                    mpus = sorted(self.Microprocessors.keys())
                    msg = "Fatal: no such MPU. Available MPUs: %s"
                    self._output(msg % ', '.join(mpus))
                    sys.exit(1)
                self.mpu_type = mpu_type

            if opt in ("-h", "--help"):
                self._usage()
                self._exit(0)

            if opt in ('-l', '--load'):
                load = value

            if opt in ('-r', '--rom'):
                rom = value

            if opt in ('-g', '--goto'):
                goto = value

            if opt in ('-w', '--debug'):
                win = True

            if opt in ('-v', '--via'):
                via = int(value, 16)

            if opt in ('-a', '--acia'):
                acia = value

        return load, rom, goto, win, via, acia

    def do_debug(self, args):
        if self.dbWin is None:
            self.dbWin = server(self, self._mpu, self.dbInt, True)
        else:
            self.dbWin.install_db(True)

    def help_debug(self):
        self._output("Open debug window.")

    def do_via(self, args):
        if args == '':
            return self.help_via()

        if isinstance(args, str):
            addr = self._address_parser.number(args)
        else:
            addr = args

        #addr = int(args, 16)
        if self.dbInt is None:
            self.dbInt = Interrupts(self, self._mpu)

        self.dbInt.addVIA(addr)

    def help_via(self):
        self._output("via <address>")
        self._output("Add a VIA at address.")

    def do_acia(self, args):
        split = shlex.split(args)
        if len(split) != 2:
            self._output(args)
            return self.help_acia()

        filename = split[1]

        #addr = self._address_parser.number(args)
        addr = int(split[0], 16)

        if self.dbInt is None:
            self.dbInt = Interrupts(self, self._mpu)

        self.dbInt.addACIA(addr, filename)

    def help_acia(self):
        self._output("acia <address> <filename>")
        self._output("Add an ACIA at address with filename for block access.")

    def do_version(self, args):
        self._output("\n65816 Debug Monitor")

    def help_version(self):
        self._output("version\t\tDisplay Py65816 version information.")

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
        self._address_parser = AddressParser(maxwidth=24)
        self._disassembler = Disassembler(self._mpu, self._address_parser)
        self._assembler = Assembler(self._mpu, self._address_parser)

    def _run(self, stopcodes):
        if self.dbWin:
            try:
                self.dbWin.do_db(stopcodes, self._breakpoints)
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

    # *** TODO: allow for 65816 registers ***
    def do_registers(self, args):
        if args == '':
            return

        pairs = re.findall('([^=,\s]*)=([^=,\s]*)', args)
        if pairs == []:
            return self._output("Syntax error: %s" % args)

        for register, value in pairs:
            if register not in ('pc', 'sp', 'a', 'x', 'y', 'p'):
                self._output("Invalid register: %s" % register)
            else:
                try:
                    intval = self._address_parser.number(value)
                except KeyError as exc: # label not found
                    self._output(exc.args[0])
                    continue
                except OverflowError as exc: # wider than address space
                    msg = "Overflow: %r too wide for register %r"
                    self._output(msg % (value, register))
                    continue

                # check size against mode/bit selection
                if register == 'p' or ((self._mpu.p & self._mpu.MS) and (register == 'a')) or ((self._mpu.p & self._mpu.IRS) and ((register == 'x') or (register == 'y'))):
                    if intval != (intval & self.byteMask):
                        msg = "Overflow: %r too wide for register %r"
                        self._output(msg % (value, register))
                        continue
#                if register == 'pc' or register == 'sp':
                else:
                    if intval != (intval & self.addrMask):
                        msg = "Overflow: %r too wide for register %r"
                        self._output(msg % (value, register))
                        continue

                setattr(self._mpu, register, intval)

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
