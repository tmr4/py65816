import socket
import time
import errno
import sys
import cmd
import re
import shlex

from py65.utils import console
from py65.utils.addressing import AddressParser
from py65.utils.conversions import itoa

class client(cmd.Cmd):
    intro = "Debug Terminal v0.0.0\nConnection from py65mon established"
    prompt = "."
    use_rawinput = False

    def __init__(self):
        self._add_shortcuts()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((socket.gethostname(), 1243))
        self.s.setblocking(False)
        self.address_parser = AddressParser(maxwidth=24)
        self.width = 72
        self.addrFmt = "%04x"
        self.byteFmt = "%02x"
        self.breakpoints = []

        cmd.Cmd.__init__(self)

    def _add_shortcuts(self):
        # uncomment shortcuts for added commands
        self._shortcuts = {'EOF':  'quit',
                           '~':    'tilde',
#                           'a':    'assemble',
                           'ab':   'add_breakpoint',
#                           'al':   'add_label',
                           'c':    'continue',
#                           'd':    'disassemble',
                           'db':   'delete_breakpoint',
#                           'dl':   'delete_label',
                           'exit': 'quit',
#                           'f':    'fill',
#                           '>':    'fill',
#                           'g':    'goto',
                           'h':    'help',
                           '?':    'help',
#                           'l':    'load',
                           'm':    'mem',
                           'q':    'quit',
                           'r':    'registers',
#                           'ret':  'return',
                           'rad':  'radix',
#                           's':    'save',
                           'shb':  'show_breakpoints',
#                           'shl':  'show_labels',
                           'w':    'width',
                           'x':    'quit',
                           'z':    'step'}

    def precmd(self, line):
        # check if server has sent a notice
        # *** TODO: not sure this is currently needed but could be with other commands. ***
        msg = self.recMsg()

        if msg != None:
            print(msg)

        return line

    def onecmd(self, line):
        line = self._preprocess_line(line)

        result = None
        try:
            result = cmd.Cmd.onecmd(self, line)
        except KeyboardInterrupt:
            print("Interrupt")
        #except Exception:
        #    (file, fun, line), t, v, tbinfo = compact_traceback()
        #    error = 'Error: %s, %s: file: %s line: %s' % (t, v, file, line)
        #    print(error)

        #if not line.startswith("quit"):
        ##    print_mpu_status()
        #    self.s.send(b"r")
        #    try:
        #        msg = self.s.recv(1024).decode("utf-8")
        #        print(msg)
        #    except IOError as e:
        #        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
        #            print('Reading error: {}'.format(str(e)))
        #            sys.exit()
#
        #    except Exception as e:
        #        print('Reading error: '.format(str(e)))
        #        sys.exit()

        return result

    def _preprocess_line(self, line):
        # command shortcuts
        for shortcut, command in self._shortcuts.items():
            if line == shortcut:
                line = command
                break

            pattern = '^%s\s+' % re.escape(shortcut)
            matches = re.match(pattern, line)
            if matches:
                start, end = matches.span()
                line = "%s %s" % (command, line[end:])
                break

        return line

    def sendCmd(self, cmd, value=0):
        self.s.send(cmd.encode()+str(value).encode().zfill(5))

    def recMsg(self):
        try:
            return self.s.recv(1024).decode()

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()

    def recVal(self):
        try:
            return int(self.s.recv(5).decode())

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()

    # Commands
    def do_add_breakpoint(self, args):
        split = shlex.split(args)
        if len(split) != 1:
            print("Syntax error: %s" % args)
            return self.help_add_breakpoint()

        address = self.address_parser.number(split[0])
        if address in self.breakpoints:
            print("Breakpoint already present at $%04X\n" % address)
        else:
            self.breakpoints.append(address)
            msg = "Breakpoint %d added at $%04X\n"
            print(msg % (len(self.breakpoints) - 1, address))
            self.sendCmd("b", address)

    def do_continue(self, args):
        self.sendCmd("c")

    def do_delete_breakpoint(self, args):
        split = shlex.split(args)
        if len(split) != 1:
            print("Syntax error: %s" % args)
            return self.help_delete_breakpoint()

        number = None
        try:
            number = int(split[0])
            if number < 0 or number > len(self.breakpoints):
                print("Invalid breakpoint number %d", number)
                return
        except ValueError:
            print("Illegal number: %s" % args)
            return

        if self.breakpoints[number] is not None:
            self.sendCmd("e", number)
            self.breakpoints[number] = None
            print("Breakpoint %d removed" % number)
        else:
            print("Breakpoint %d already removed" % number)

    def do_help(self, args):
        args = self._shortcuts.get(args.strip(), args)
        return cmd.Cmd.do_help(self, args)

    def do_mem(self, args):
        split = shlex.split(args)
        if len(split) != 1:
            return self.help_mem()

        start, end = self.address_parser.range(split[0])

        line = self.addrFmt % start + ":"
        for address in range(start, end + 1):
            self.sendCmd("m", address)
            time.sleep(.1) # allow server to process  (*** .05 too short ***)
            byte = self.recMsg()

            if byte != None:
                more = "  " + self.byteFmt % int(byte)

                exceeded = len(line) + len(more) > self.width
                if exceeded:
                    print(line)
                    line = self.addrFmt % address + ":"
                line += more
        print(line)

    def do_quit(self, args):
        self.sendCmd("q")
        print('')
        return 1

    def do_radix(self, args):
        radixes = {'Hexadecimal': 16, 'Decimal': 10, 'Octal': 8, 'Binary': 2}

        if args != '':
            new = args[0].lower()
            changed = False
            for name, radix in radixes.items():
                if name[0].lower() == new:
                    self.address_parser.radix = radix
                    changed = True
            if not changed:
                print("Illegal radix: %s" % args)

        for name, radix in radixes.items():
            if self.address_parser.radix == radix:
                print("Default radix is %s" % name)

    def do_registers(self, args):
        self.sendCmd("r")
        time.sleep(.1) # allow server to process  (*** .05 too short ***)
        print(self.recMsg())

    #def do_reset(self, args):
    #    self.sendCmd("s")

    def do_show_breakpoints(self, args):
        for i, address in enumerate(self.breakpoints):
            if address is not None:
                bpinfo = "Breakpoint %d: $%04X" % (i, address)
                print(bpinfo)

    def do_step(self, args):
        self.sendCmd("z")
        time.sleep(.1) # allow server to process step (*** .01 too short ***)
        print(self.recMsg())

    def do_tilde(self, args):
        if args == '':
            return self.help_tilde()

        try:
            num = self.address_parser.number(args)
            print("+%u" % num)
            print("$" + self.byteFmt % num)
            print("%04o" % num)
            print(itoa(num, 2).zfill(8))
        except KeyError:
            print("Bad label: %s" % args)
        except OverflowError:
            print("Overflow error: %s" % args)

    def do_version(self, args):
        print("\nDebug Terminal v0.0.0")

    def do_width(self, args):
        if args != '':
            try:
                new_width = int(args)
                if new_width >= 10:
                    self.width = new_width
                    self.sendCmd("w", new_width)
                else:
                    print("Minimum terminal width is 10")
            except ValueError:
                print("Illegal width: %s" % args)

        print("Terminal width is %d" % self.width)

    # Help
    def help_add_breakpoint(self):
        print("add_breakpoint <address|label>")
        print("Add a breakpoint on execution at the given address or label")

    def help_continue(self):
        print("Continue execution from breakpoint.\n")

    def help_delete_breakpoint(self):
        print("delete_breakpoint <number>")
        print("Delete the breakpoint on execution marked by the given number")

    def help_help(self):
        print("help\t\tPrint a list of available command.\n")
        print("help <action>\tPrint help for <command>.\n")

    def help_mem(self):
        print("mem <address_range>")
        print("Display the contents of memory.")
        print('Range is specified like "<start:end>".')

    def help_quit(self):
        print("To quit the debug window, type ^D or use the quit command.\n")
        print("Your program will continue running or break to the monitor if it's stopped.\n")
#        print("To restart the debug window press <ESC>D or <ESC>d.\n")
        # *** <ESC>q in program window will break to $fff9 when debug window is open. Otherwise it breaks to monitor ***

    def help_radix(self):
        print("radix [H|D|O|B]")
        print("Set default radix to hex, decimal, octal, or binary.")
        print("With no argument, the current radix is printed.")

    def help_registers(self):
        self._output("Display register values.")

    #def help_reset(self):
    #    self._output("reset\t\tReset the microprocessor")

    def help_show_breakpoints(self):
        print("show_breakpoints")
        print("Lists the currently assigned breakpoints")

    def help_step(self):
        print("Enter single step mode.")
        print("Single-step through instructions afterwards by pressing Enter.")

    def help_tilde(self):
        print("~ <number>")
        print("Display a number in decimal, hex, octal, and binary.")

    def help_version(self):
        print("version\t\tDisplay Py65 version information.\n")

    def help_width(self):
        print("width <columns>")
        print("Set the width used by some commands to wrap output.")
        print("With no argument, the current width is printed.")

if __name__ == "__main__":
    c = client()
    c.cmdloop()