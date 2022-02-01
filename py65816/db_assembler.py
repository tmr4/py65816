import re
from py65.utils.addressing import AddressParser

#from py65.assembler import Assembler

#class dbAssembler(Assembler):
class dbAssembler():

    # w/ long addressing
    Statement = re.compile(r'^([A-z]{3}[0-7]?\s+[\[\(]?\s*)'
                        r'([^,\s\)\]]+)'
                        r'(\s*[,xXyY\s]*[\)\]]?[,xXyY\s]*)$')

    # new addressing modes
    Addressing = (
        ('abs', "$FFFF"),
        ('abx', "$FFFF,X"),
        ('aby', "$FFFF,Y"),
        ('abi', "($FFFF)"),
        ('aix', "($FFFF,X)"),
        ('ail', "[$FFFF]"),
        ('abl', "$FFFFFF"),
        ('alx', "$FFFFFF,X"),
        ('acc', ""),
        ('acc', "A"),
        ('blk', "$FF,$FF"),
        ('dpg', "$FF"),
        ('dpx', "$FF,X"),
        ('dpy', "$FF,Y"),
        ('dpi', "($FF)"),
        ('dix', "($FF,X)"),
        ('dil', "[$FF]"),
        ('diy', "($FF),Y"),
        ('dly', "[$FF],Y"),
        ('imm', "#$FF"),
        ('imp', ""),
        ('pcr', "$FF"),
        ('pcr', "$FFFF"),   # for branch by label
        ('prl', "$FFFF"),
        ('siy', "($FF,S),Y"),
        ('ska', "$FFFF"),
        ('ski', "$FF"),
        ('spc', "$FFFF"),
        ('stk', ""),
        ('str', "$FF,S"),
    )

    # might as well just get the whole thing
    def __init__(self, mpu, address_parser=None):
        """ If a configured AddressParser is passed, symbolic addresses
        may be used in the assembly statements.
        """
        self._mpu = mpu

        if address_parser is None:
            address_parser = AddressParser(maxwidth=24)
        self._address_parser = address_parser

        self._addressing = []
        numchars = mpu.BYTE_WIDTH / 4  # 1 byte = 2 chars in hex
        for mode, format in self.Addressing:
            pat = "^" + re.escape(format) + "$"
            pat = pat.replace('00', '0{%d}' % numchars)
            pat = pat.replace('FF', '([0-9A-F]{%d})' % numchars)
            self._addressing.append([mode, re.compile(pat)])

#        super().__init__(mpu, address_parser)

    def assemble(self, statement, pc=0000):
        """ Assemble the given assembly language statement.  If the statement
        uses relative addressing, the program counter (pc) must also be given.
        The result is a list of bytes.  Raises when assembly fails.
        """
        opcode, operand = self.normalize_and_split(statement)

        for mode, pattern in self._addressing:
            match = pattern.match(operand)

            if match:
                # check if opcode supports this addressing mode
                try:
                    bytes = [self._mpu.disassemble.index((opcode, mode))]
                except ValueError:
                    continue

                operands = match.groups()

                if mode == 'pcr' or (mode == 'prl' and len(operands) == 1):
                    # relative branch
                    absolute = int(''.join(operands), 16)
                    relative = (absolute - pc) - 2
                    relative = relative & self._mpu.byteMask
                    operands = [(self._mpu.BYTE_FORMAT % relative)]

                if mode == 'prl':
                    # relative branch
                    absolute = int(''.join(operands), 16)
                    relative = (absolute - pc) - 3
                    relative = relative & self._mpu.addrMask
                    operands = [(self._mpu.ADDR_FORMAT % (relative & self._mpu.byteMask)),
                                (self._mpu.ADDR_FORMAT % (relative >> self._mpu.BYTE_WIDTH))]

                # don't swap block move bytes
                elif len(operands) == 2 and  mode != 'blk':
                    # swap bytes
                    operands = (operands[1], operands[0])

                # handle long addresses
                elif len(operands) == 3:
                    # swap bytes
                    operands = (operands[2], operands[1], operands[0])

                operands = [int(hex, 16) for hex in operands]
                bytes.extend(operands)

                # raise if the assembled bytes would exceed top of memory
                # allow for long memory addressing
#                if (pc + len(bytes)) > (2 ** self._mpu.ADDR_WIDTH):
                if (pc + len(bytes)) > (2 ** self._mpu.ADDRL_WIDTH):
                    raise OverflowError

                return bytes

        # assembly failed
        raise SyntaxError(statement)

    # need to maintain direct page addressing format
    def normalize_and_split(self, statement):
        """ Given an assembly language statement like "lda $c12,x", normalize
            the statement by uppercasing it, removing unnecessary whitespace,
            and parsing the address part using AddressParser.  The result of
            the normalization is a tuple of two strings (opcode, operand).
        """
        statement = ' '.join(str.split(statement))

        # normalize target in operand
        match = self.Statement.match(statement)
        if match:
            before, target, after = match.groups()

            # target is an immediate value
            if target.startswith('#'):
                try:
                    if target[1] in ("'", '"'): # quoted ascii character
                        number = ord(target[2])
                    else:
                        number = self._address_parser.number(target[1:])
                except IndexError:
                    raise SyntaxError(statement)

                if (number < 0) or (number > self._mpu.byteMask):
                    raise OverflowError
                statement = before + '#$' + self._mpu.BYTE_FORMAT % number

            # target is the accumulator
            elif target in ('a', 'A'):
                pass

            # target is an address or label
            else:
                address = self._address_parser.number(target)
                # for now, assume all addresses < 256 are direct page
                if address >= 0xffff:
#                    statement = before + '$' + self._mpu.ADDRL_FORMAT % address + after
                    statement = before + '$' + '%06x' % address + after
                elif address >= 0xff:
                    statement = before + '$' + self._mpu.ADDR_FORMAT % address + after
                else:
                    statement = before + '$' + self._mpu.BYTE_FORMAT % address + after

        # separate opcode and operand
        splitted = statement.split(" ", 2)
        opcode = splitted[0].strip().upper()
        if len(splitted) > 1:
            operand = splitted[1].strip().upper()
        else:
            operand = ''
        return (opcode, operand)
