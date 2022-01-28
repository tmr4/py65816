
from py65.disassembler import Disassembler

class dbDisassembler(Disassembler):

    def __init__(self, mpu, address_parser=None):
        super().__init__(mpu, address_parser)

    def instruction_at(self, pc):
        """ Disassemble the instruction at PC and return a tuple
        containing (instruction byte count, human readable text)
        """

        instruction = self._mpu.ByteAt(pc)
        disasm, addressing = self._mpu.disassemble[instruction]

        if addressing == 'acc':
            disasm += ' A'
            length = 1

        elif addressing == 'abs':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' ' + address_or_label
            length = 3

        elif addressing == 'abx':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' %s,X' % address_or_label
            length = 3

        elif addressing == 'aby':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' %s,Y' % address_or_label
            length = 3

        elif addressing == 'imm':
            byte = self._mpu.ByteAt(pc + 1)
            disasm += ' #$' + self.byteFmt % byte
            length = 2

        elif addressing == 'imp':
            length = 1

        elif addressing == 'ind':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' (%s)' % address_or_label
            length = 3

        elif addressing == 'iny':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' (%s),Y' % address_or_label
            length = 2

        elif addressing == 'inx':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' (%s,X)' % address_or_label
            length = 2

        elif addressing == 'iax':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' (%s,X)' % address_or_label
            length = 3

        elif addressing == 'rel':
            opv = self._mpu.ByteAt(pc + 1)
            targ = pc + 2
            if opv & (1 << (self.byteWidth - 1)):
                targ -= (opv ^ self.byteMask) + 1
            else:
                targ += opv
            targ &= self.addrMask

            address_or_label = self._address_parser.label_for(
                targ, '$' + self.addrFmt % targ)
            disasm += ' ' + address_or_label
            length = 2

        elif addressing == 'zpi':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '($' + self.byteFmt % zp_address + ')')
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'zpg':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'zpx':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' %s,X' % address_or_label
            length = 2

        elif addressing == 'zpy':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' %s,Y' % address_or_label
            length = 2

        # 65816 specific address modes
        # *** TODO: many of these duplicate above except for address mode mnemonic.
        # Consider consolidating ***

        elif addressing == 'abi':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' (%s)' % address_or_label
            length = 3

        elif addressing == 'aix':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' (%s,X)' % address_or_label
            length = 3

        elif addressing == 'ail':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' [%s]' % address_or_label
            length = 3

        elif addressing == 'abl':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' %s' % address_or_label
            length = 4

        elif addressing == 'alx':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' %s,X' % address_or_label
            length = 4

        elif addressing == 'blk':
            source = self._mpu.ByteAt(pc + 1)
            dest = self._mpu.ByteAt(pc + 2)
            source_bank = self._address_parser.label_for(
                source, '$' + self.byteFmt % source)
            dest_bank = self._address_parser.label_for(
                dest, '$' + self.byteFmt % dest)
            disasm += ' %s,%s' % (source_bank, dest_bank)
            length = 3

        elif addressing == 'dpg':
            dp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                dp_address, '$' + self.byteFmt % dp_address)
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'dpx':
            dp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                dp_address, '$' + self.byteFmt % dp_address)
            disasm += ' %s,X' % address_or_label
            length = 2

        elif addressing == 'dpy':
            dp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                dp_address, '$' + self.byteFmt % dp_address)
            disasm += ' %s,Y' % address_or_label
            length = 2

        elif addressing == 'dix':
            dp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                dp_address, '$' + self.byteFmt % dp_address)
            disasm += ' (%s,X)' % address_or_label
            length = 2

        elif addressing == 'dpi':
            dp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                dp_address, '($' + self.byteFmt % dp_address + ')')
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'dil':
            dp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                dp_address, '[$' + self.byteFmt % dp_address + ']')
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'diy':
            dp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                dp_address, '$' + self.byteFmt % dp_address)
            disasm += ' (%s),Y' % address_or_label
            length = 2

        elif addressing == 'dly':
            dp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                dp_address, '$' + self.byteFmt % dp_address)
            disasm += ' [%s],Y' % address_or_label
            length = 2

        elif addressing == 'pcr':
            opv = self._mpu.ByteAt(pc + 1)
            targ = pc + 2
            if opv & (1 << (self.byteWidth - 1)):
                targ -= (opv ^ self.byteMask) + 1
            else:
                targ += opv
            targ &= self.addrMask

            address_or_label = self._address_parser.label_for(
                targ, '$' + self.addrFmt % targ)
            disasm += ' ' + address_or_label
            length = 2

        elif addressing == 'prl':
            # *** CHECK ***
            opv = self._mpu.WordAt(pc + 1)
            targ = pc + 3
            if opv & (1 << (self.byteWidth - 1)):
                targ -= (opv ^ self.byteMask) + 1
            else:
                targ += opv
            targ &= self.addrMask

            address_or_label = self._address_parser.label_for(
                targ, '$' + self.addrFmt % targ)
            disasm += ' ' + address_or_label
            length = 3

        elif addressing == 'ska':
            data = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                data, '$' + self.addrFmt % data)
            disasm += ' ' + address_or_label
            length = 3

        elif addressing == 'ski':
            byte = self._mpu.ByteAt(pc + 1)
            disasm += ' #$' + self.byteFmt % byte
            length = 2

        elif addressing == 'stk':
            length = 1

        elif addressing == 'str':
            sp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                sp_address, '$' + self.byteFmt % sp_address)
            disasm += ' %s,S' % address_or_label
            length = 2

        elif addressing == 'siy':
            sp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                sp_address, '$' + self.byteFmt % sp_address)
            disasm += ' (%s,S),Y' % address_or_label
            length = 2

        else:
            msg = "Addressing mode: %r" % addressing
            raise NotImplementedError(msg)

        return (length, disasm)
