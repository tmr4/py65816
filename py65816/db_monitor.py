"""py65816mon -- interact with a simulated 65816-based system

Usage: %s [options]

Options:
-h, --help             : Show this message
-d, --debug            : Toggle debug window
-m, --mpu <device>     : Choose which MPU device (default is 6502)
-l, --load <file>      : Load a file at address 0
-r, --rom <file>       : Load a rom at the top of address space and reset into it
-g, --goto <address>   : Perform a goto command after loading any files
-i, --input <address>  : define location of getc (default $f004)
-o, --output <address> : define location of putc (default $f001)
"""

import getopt
import sys

from py65.utils import console
from py65.monitor import Monitor

from py65816.devices.mpu65c816 import MPU as CMOS65C816
from py65816.db_server import db_server as server

class dbMonitor(Monitor):

    Monitor.Microprocessors["65C816"] = CMOS65C816

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
        super()._reset(mpu_type, getc_addr, putc_addr)

        if self.dbWin:
            self.s = server(self, self._mpu)

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
