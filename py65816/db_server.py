import os
import select
import socket
import subprocess
import time
import threading

from py65.utils.conversions import itoa

class db_server():

    def __init__(self, mon, mpu, interrupts, dbWin=False):
#    def __init__(self, mon, mpu):
        self.mon = mon
        self.mpu = mpu

        # *** TODO: consider if the debug window needs to be aware of interrupts ***
        self.interrupts = interrupts

        self.SThread = False
        self.dbOpt = 0
        self.dbWin = False

        self.s = None
        self.sockets_list = []

#        if interrupts.via.check_debug():
#            self.install_db()
        self.install_db(dbWin)

    def install_db(self, dbWin):
        if dbWin:
            if not self.dbWin:
                self.install_client()
                self.install_server()

        self.dbWin = dbWin

#    def check_quit(self):
#        return self.interrupts.via.quit

    def client(self):
        dir = os.path.dirname(__file__)
        client_path = os.path.join(dir, 'db_client.py')
        self.p = subprocess.Popen('python ' + client_path, 
            #stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE)

    def install_client(self):
        if self.s == None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((socket.gethostname(), 1243))
            self.s.listen(5)
            self.sockets_list = [self.s]

        client_thread = threading.Thread(name="Client", target=self.client, args=(), daemon=True)
        client_thread.start()

        self.clientsocket, address = self.s.accept()
        self.sockets_list.append(self.clientsocket)

    def install_server(self):
        def server_thread():
            mpu = self.mpu
            mon = self.mon
            while(self.SThread):
                read_sockets, _, exception_socket = select.select(self.sockets_list, [], self.sockets_list)
                for clientsocket in read_sockets:
                    if clientsocket == self.clientsocket:
                        msg = self.recMsg()
                        if msg:
                            cmd = msg[:1].decode()
                            if cmd != '':
                                value = int(msg[1:].decode())
                                if cmd == 'b': # set breakpoint
                                    mon._breakpoints.append(value)
                                    self.breakpoints.add(value)
                                elif cmd == 'c': # continue
                                    self.dbOpt = 0
                                elif cmd == 'd': # disassemble current instruction
                                    x = 1 # *** TODO: ***
                                elif cmd == 'e': # delete breakpoint
                                    mon._breakpoints[value] = None
                                    mon._breakpoints.append(value)
                                    self.breakpoints = set(mon._breakpoints)
                                elif cmd == 'm': # mem
                                    byte = mpu.memory[value]
                                    self.sendVal(byte)
                                elif cmd == 'q': # quit debug window (program continues)
                                    #self.dbOpt = 0
#                                    self.interrupts.via.check_debug(False)
                                    self.dbWin = False
                                    self.SThread = False
                                elif cmd == 'r': # registers
                                    msg = "\n" + repr(mpu) + "\n"
                                    self.sendMsg(msg)
                                #elif cmd == 's': # reset
                                #    klass = self.mpu.__class__
                                #    self.mon._reset(mpu_type=klass)
                                elif cmd == 'w': # width
                                    self.mon._width = value
                                elif cmd == 'z': # step
                                    self.dbOpt = 2
                                    #msg = mpu.__repr__()
                                    length, disasm = mon._disassembler.instruction_at(mpu.pc)
                                    msg = mon._format_disassembly(mpu.pc, length, disasm)
                                    self.sendMsg(msg)
                                #else:   # print registers
                            else:   # quit
                                self.SThread = False
                                self.dbWin = False
#                                self.interrupts.via.check_debug(False)
                        else:   # debug window was closed or connection lost
                            self.SThread = False
#                            self.interrupts.via.check_debug(False)

        if not self.SThread:
            t = threading.Thread(target=server_thread, daemon = True)
            self.SThread = True
            t.start()
        else:
            self.SThread = False

    def sendMsg(self, msg):
        self.clientsocket.send(bytes(msg,"utf-8"))

    def sendVal(self, value):
        self.clientsocket.send(str(value).encode().zfill(5))

    def recMsg(self):
        try:
            msg = self.clientsocket.recv(6)
            return msg
        except:
            return False

    def do_db(self, stopcodes, breakpoints):
        self.stopcodes = set(stopcodes)
        self.breakpoints = set(breakpoints)
        mpu = self.mpu
        mem = mpu.memory

        while self.step():
            if mpu.ADDRL_WIDTH > mpu.ADDR_WIDTH:
                pc = (mpu.pbr << mpu.ADDR_WIDTH) + mpu.pc
            else:
                pc = mpu.pc
            if mem[pc] in self.stopcodes:
                if self.dbOpt != 1 and self.SThread:
                    self.sendMsg(f"Stopcode {itoa(mem[pc], 16)} hit at {itoa(pc, 16)} ")
                self.dbOpt = 1
            if self.breakpoints:
                if pc in self.breakpoints:
                    if self.dbOpt != 1:
                        if  self.SThread:
                            self.sendMsg(f"Breakpoint hit at {itoa(pc, 16)} ")
                        else:
                            self.mon._output(f"Breakpoint hit at {itoa(pc, 16)} ")
                        self.dbOpt = 1

    def step(self):
        if not self.SThread:
#            if self.interrupts.via.check_debug():
#                self.install_db()
#
#            if self.check_quit():
#                self.interrupts.via.check_debug(False)
#                return False
            if self.dbWin:
                self.install_db()

        mpu = self.mpu
        mon = self.mon
        if self.dbOpt == 0: # normal step
            mpu.step()
        elif self.dbOpt == 1: # stopped at breakpoint or stopcode, or single stepping
            if self.SThread:
                time.sleep(1) # just delay for a bit (only a continue can get us out of here)
            else:
                return False # *** TODO: enable SRThread when at breakpoint ***
        elif self.dbOpt == 2: # single step
            mpu.step()
            self.dbOpt = 1

        return True


