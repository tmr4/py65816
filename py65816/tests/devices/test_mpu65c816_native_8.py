import unittest # python -m unittest discover -p "*816_native_8.py"
import sys
from py65816.devices.mpu65c816 import MPU
from py65816.tests.devices.mpu65816_Common_tests_6502 import Common6502Tests
from py65816.tests.devices.mpu65816_Common_tests_65c02 import Common65C02Tests
from py65816.tests.devices.mpu65816_Common_tests_native import Common65816NativeTests

# x tests
class MPUTests(unittest.TestCase, Common6502Tests, Common65C02Tests, Common65816NativeTests):
#class MPUTests(unittest.TestCase):
    """CMOS 65C816 Tests - Native Mode - 8 Bit"""

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertTrue('65C816' in repr(mpu))

    # Native Mode - 8 bit

    # Page Bounday Wrap Tests
    def test_dpx_no_wraps_page_boundary_when_dl_zero(self):
        mpu = self._make_mpu()
        mpu.dpr = 0x0100
        mpu.x = 1
        self._write(mpu.memory, 0x00ff, (0x34, 0x12))
        self._write(mpu.memory, 0x01ff, (0xcd, 0xab))
        # $0000 LDA $ff,X
        self._write(mpu.memory, 0x0000, (0xb5, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xab, mpu.a)

    def test_dpx_no_wrap_page_boundary_when_dl_not_zero(self):
        mpu = self._make_mpu()
        mpu.dpr = 0x0101
        mpu.x = 0
        self._write(mpu.memory, 0x00ff, (0x34, 0x12))
        self._write(mpu.memory, 0x01ff, (0xcd, 0xab))
        # $0000 LDA $ff,X
        self._write(mpu.memory, 0x0000, (0xb5, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xab, mpu.a)

    def test_dpi_no_wrap_page_boundary_when_dl_zero(self):
        mpu = self._make_mpu()
        mpu.dpr = 0x0100
        self._write(mpu.memory, 0x0100, (0xcd, 0xab))
        self._write(mpu.memory, 0x01ff, (0x34, 0x12))
        self._write(mpu.memory, 0x1234, (0x78, 0x56))
        self._write(mpu.memory, 0xabcd, (0xbc, 0x9a))
        self._write(mpu.memory, 0xcd34, (0x10, 0x20))
        # $0000 LDA ($ff)
        self._write(mpu.memory, 0x0000, (0xb2, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x78, mpu.a)

    def test_dix_no_wraps_page_boundary_when_dl_zero(self):
        mpu = self._make_mpu()
        mpu.dpr = 0x0100
        mpu.x = 1
        self._write(mpu.memory, 0x0100, (0xcd, 0xab))
        self._write(mpu.memory, 0x01ff, (0x34, 0x12))
        self._write(mpu.memory, 0x1234, (0x78, 0x56))
        self._write(mpu.memory, 0xabcd, (0xbc, 0x9a))
        self._write(mpu.memory, 0xcd34, (0x10, 0x20))
        # $0000 LDA ($ff,X)
        self._write(mpu.memory, 0x0000, (0xa1, 0xfe))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x78, mpu.a)

    def test_no_stack_wrap(self):
        mpu = self._make_mpu()
        mpu.sp = 0x01ff
        self._write(mpu.memory, 0x00ff, (0x34, 0x12))
        self._write(mpu.memory, 0x01ff, (0xcd, 0xab))
        # $000 PLA
        mpu.memory[0x0000] = 0x68
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xab, mpu.a)

    # Bank Bounday Wrap Tests

    def test_dpx_wraps_at_bank_zero_boundary(self):
        mpu = self._make_mpu()
        mpu.pc = 0x0100
        mpu.dpr = 0xff01
        mpu.x = 0x00
        self._write(mpu.memory, 0x0000, (0x34, 0x12))
        self._write(mpu.memory, 0x10000, (0xcd, 0xab))
        # $0000 LDA $ff,X
        self._write(mpu.memory, 0x0100, (0xb5, 0xff))
        mpu.step()
        self.assertEqual(0x0102, mpu.pc)
        self.assertEqual(0x34, mpu.a)

    def test_dpi_dp_wraps_at_bank_zero_boundary(self):
        mpu = self._make_mpu()
        mpu.pc = 0x0100
        mpu.dpr = 0xff01
        mpu.dbr = 0x01
        self._write(mpu.memory, 0x0000, (0x34, 0x12))
        self._write(mpu.memory, 0xffff, (0xcd, 0xab))
        self._write(mpu.memory, 0x011234, (0x78, 0x56))
        self._write(mpu.memory, 0x01abcd, (0xbc, 0x9a))
        self._write(mpu.memory, 0x0134cd, (0x10, 0x20))
        # $0000 LDA ($ff)
        self._write(mpu.memory, 0x0100, (0xb2, 0xff))
        mpu.step()
        self.assertEqual(0x0102, mpu.pc)
        self.assertEqual(0x78, mpu.a)

    def test_dpi_indaddr_wraps_at_bank_zero_boundary(self):
        mpu = self._make_mpu()
        mpu.pc = 0x0100
        mpu.dpr = 0xff01
        mpu.dbr = 0x01
        self._write(mpu.memory, 0x0000, (0x34, 0x12))
        self._write(mpu.memory, 0xffff, (0xcd, 0xab))
        self._write(mpu.memory, 0x011234, (0x78, 0x56))
        self._write(mpu.memory, 0x01abcd, (0xbc, 0x9a))
        self._write(mpu.memory, 0x0134cd, (0x10, 0x20))
        # $0000 LDA ($ff)
        self._write(mpu.memory, 0x0100, (0xb2, 0xfe))
        mpu.step()
        self.assertEqual(0x0102, mpu.pc)
        self.assertEqual(0x10, mpu.a)

    def test_dix_wraps_at_bank_zero_boundary(self):
        mpu = self._make_mpu()
        mpu.pc = 0x0100
        mpu.dpr = 0xff01
        mpu.dbr = 0x01
        mpu.x = 0x00
        self._write(mpu.memory, 0x0000, (0x34, 0x12))
        self._write(mpu.memory, 0x10000, (0xcd, 0xab))
        self._write(mpu.memory, 0x011234, (0x78, 0x56))
        self._write(mpu.memory, 0x01abcd, (0xbc, 0x9a))
        self._write(mpu.memory, 0x0134cd, (0x10, 0x20))
        # $0000 LDA ($ff,X)
        self._write(mpu.memory, 0x0100, (0xa1, 0xff))
        mpu.step()
        self.assertEqual(0x0102, mpu.pc)
        self.assertEqual(0x78, mpu.a)

    def test_dil_no_wraps_at_page_boundary(self):
        mpu = self._make_mpu()
        mpu.pc = 0x0100
        mpu.dpr = 0xff00
        mpu.dbr = 0x01
        self._write(mpu.memory, 0x0000, (0x34, 0x01))
        self._write(mpu.memory, 0xff00, (0xab, 0x01))
        self._write(mpu.memory, 0xffff, (0xcd, 0xab, 0x01))
        self._write(mpu.memory, 0x011234, (0x78, 0x56))
        self._write(mpu.memory, 0x01abcd, (0xbc, 0x9a))
        self._write(mpu.memory, 0x0134cd, (0x10, 0x20))
        # $0000 LDA ($ff)
        self._write(mpu.memory, 0x0100, (0xa7, 0xff))
        mpu.step()
        self.assertEqual(0x0102, mpu.pc)
        self.assertEqual(0x10, mpu.a)

    def test_dil_indaddr_wraps_at_bank_zero_boundary_1_byte(self):
        mpu = self._make_mpu()
        mpu.pc = 0x0100
        mpu.dpr = 0xff00
        mpu.dbr = 0x01
        self._write(mpu.memory, 0x0000, (0x01, 0x34, 0x01))
        self._write(mpu.memory, 0xff00, (0x01, 0xab, 0x01))
        self._write(mpu.memory, 0xfffe, (0xcd, 0xab, 0x01))
        self._write(mpu.memory, 0x011234, (0x78, 0x56))
        self._write(mpu.memory, 0x01abcd, (0xbc, 0x9a))
        self._write(mpu.memory, 0x0134cd, (0x10, 0x20))
        # $0000 LDA ($fe)
        self._write(mpu.memory, 0x0100, (0xa7, 0xfe))
        mpu.step()
        self.assertEqual(0x0102, mpu.pc)
        self.assertEqual(0xbc, mpu.a)

    def test_dil_indaddr_wraps_at_bank_zero_boundary_2_bytes(self):
        mpu = self._make_mpu()
        mpu.pc = 0x0100
        mpu.dpr = 0xff01
        mpu.dbr = 0x01
        self._write(mpu.memory, 0x0000, (0x34, 0x01))
        self._write(mpu.memory, 0xff00, (0xab, 0x01))
        self._write(mpu.memory, 0xffff, (0xcd, 0xab, 0x01))
        self._write(mpu.memory, 0x011234, (0x78, 0x56))
        self._write(mpu.memory, 0x01abcd, (0xbc, 0x9a))
        self._write(mpu.memory, 0x0134cd, (0x10, 0x20))
        # $0000 LDA ($fe)
        self._write(mpu.memory, 0x0100, (0xa7, 0xfe))
        mpu.step()
        self.assertEqual(0x0102, mpu.pc)
        self.assertEqual(0x10, mpu.a)

    def test_pc_wraps_bank_zero_boundary(self):
        mpu = self._make_mpu()
        mpu.pc = 0xffff
        mpu.a = 0xff
        mpu.x = 0x11
        # $ffff TXA
        mpu.memory[0xffff] = 0x8a
        mpu.step()
        self.assertEqual(0x0000, mpu.pc)
        self.assertEqual(0x11, mpu.a)

    def test_pc_wraps_bank_k_boundary(self):
        mpu = self._make_mpu()
        mpu.pc = 0xffff
        mpu.pbr = 0x01
        mpu.a = 0xff
        mpu.x = 0x11
        # $ffff TXA
        mpu.memory[0x01ffff] = 0x8a
        mpu.step()
        self.assertEqual(0x0000, mpu.pc)
        self.assertEqual(0x01, mpu.pbr)
        self.assertEqual(0x11, mpu.a)



    # Reset

    def test_reset_sets_registers_to_initial_states(self):
        # W65C816S Datasheet, Nov 9, 2018, section 2.25
        mpu = self._make_mpu()
        mpu.dpr = 0xFFFF
        mpu.dbr = 0xFF
        mpu.pbr = 0xFF
        mpu.mode = 0
        mpu.p = mpu.DECIMAL
        self._write(mpu.memory, 0xFFFC, (0x34, 0x12)) # reset vector
        
        # reset doesn't initialize a,x,y,sp
        # but sets high x,y bytes to 0 and high sp byte to 1
        # these can't be explicitly tested since I don't model individual bytes
        # also can't test A since I initialize it so it's in a known state
        # would be interesting to see what the chip actually does with A
        #mpu.a = 0xFFFF 
        #mpu.x = 0xFFFF 
        #mpu.y = 0xFFFF 
        #mpu.sp = 0xFFFF 

        mpu.reset()
        self.assertEqual(1, mpu.mode)
        self.assertEqual(0, mpu.dpr)
        self.assertEqual(0, mpu.dbr)
        self.assertEqual(0, mpu.pbr)
        #self.assertEqual(0xFFFF, mpu.a)
        #self.assertEqual(0x00, mpu.x & 0xff00)
        #self.assertEqual(0x00, mpu.y & 0xff00)
        #self.assertEqual(0x100, mpu.sp & 0xff00)
        self.assertEqual(mpu.BREAK | mpu.UNUSED | mpu.INTERRUPT, mpu.p) # includes mpu.DECIMAL test
        #self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY) # the datasheet show carry set but indicates it doesn't initialize it *** TODO: what does the hardware really do? ***
        self.assertEqual(0x1234, mpu.pc)

    # BRK

    def test_brk_clears_decimal_flag(self):
        mpu = self._make_mpu()
        mpu.p = mpu.DECIMAL
        # $C000 BRK
        mpu.memory[0xC000] = 0x00
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.DECIMAL)

    def test_brk_interrupt(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFFE6, (0x00, 0x04))

        self._write(mpu.memory, 0x0000, (0xA9, 0x01,   # LDA #$01
                                         0x00, 0xEA,   # BRK + skipped byte
                                         0xEA, 0xEA,   # NOP, NOP
                                         0xA9, 0x03))  # LDA #$03

        self._write(mpu.memory, 0x0400, (0xA9, 0x02,   # LDA #$02
                                         0x40))        # RTI

        mpu.step()  # LDA #$01
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x0002, mpu.pc)
        mpu.step()  # BRK
        self.assertEqual(0x0400, mpu.pc)
        mpu.step()  # LDA #$02
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0x0402, mpu.pc)
        mpu.step()  # RTI

        self.assertEqual(0x0004, mpu.pc)
        mpu.step()  # A NOP
        mpu.step()  # The second NOP

        mpu.step()  # LDA #$03
        self.assertEqual(0x03, mpu.a)
        self.assertEqual(0x0008, mpu.pc)

    def test_brk_pushes_pc_plus_2_and_status_then_sets_pc_to_irq_vector(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFFE6, (0xCD, 0xAB))
        # $C000 BRK
        mpu.memory[0xC000] = 0x00
        mpu.pc = 0xC000
        p = mpu.p
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

        self.assertEqual(0x00, mpu.memory[0x1FF])  # PBR
        self.assertEqual(0xC0, mpu.memory[0x1FE])  # PCH
        self.assertEqual(0x02, mpu.memory[0x1FD])  # PCL
        self.assertEqual(mpu.p, mpu.memory[0x1FC])  # Status
        self.assertEqual(0x1FB, mpu.sp)

        self.assertEqual(mpu.MS | mpu.IRS | mpu.INTERRUPT, mpu.p)

    # IRQ and NMI handling (very similar to BRK)

    def test_irq_pushes_pbr_pc_and_correct_status_then_sets_pc_to_irq_vector(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFFEA, (0x88, 0x77))
        self._write(mpu.memory, 0xFFEE, (0xCD, 0xAB))

        mpu.pCLR(mpu.INTERRUPT) # enable interrupts
        mpu.pc = 0xC123
        mpu.pbr = 1
        mpu.irq()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x1FF])  # PBR
        self.assertEqual(0xC1, mpu.memory[0x1FE])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FD])  # PCL
        self.assertEqual(mpu.MS | mpu.IRS, mpu.memory[0x1FC])  # Status
        self.assertEqual(0x1FB, mpu.sp)
        self.assertEqual(0, mpu.pbr)
        self.assertEqual(mpu.MS | mpu.IRS | mpu.INTERRUPT, mpu.p)
        self.assertEqual(7, mpu.processorCycles)

    def test_nmi_pushes_pc_and_correct_status_then_sets_pc_to_nmi_vector(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFFEA, (0x88, 0x77))
        self._write(mpu.memory, 0xFFEE, (0xCD, 0xAB))
        mpu.p |= mpu.INTERRUPT # disable interrupts
        mpu.pc = 0xC123
        mpu.pbr = 1
        mpu.nmi()
        self.assertEqual(0x7788, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x1FF])  # PBR
        self.assertEqual(0xC1, mpu.memory[0x1FE])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FD])  # PCL
        self.assertEqual(mpu.MS | mpu.IRS | mpu.INTERRUPT, mpu.memory[0x1FC])  # Status
        self.assertEqual(0x1FB, mpu.sp)
        self.assertEqual(0, mpu.pbr)
        self.assertEqual(mpu.MS | mpu.IRS | mpu.INTERRUPT, mpu.p)
        self.assertEqual(7, mpu.processorCycles)

    # JMP Indirect

    def test_jmp_ind_does_not_have_page_wrap_bug(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x10FF, (0xCD, 0xAB))
        # $0000 JMP ($10FF)
        self._write(mpu.memory, 0, (0x6c, 0xFF, 0x10))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # JSR

    def test_jsr_pushes_pc_plus_2_and_sets_pc(self):
        mpu = self._make_mpu()
        # $C000 JSR $FFD2
        self._write(mpu.memory, 0xC000, (0x20, 0xD2, 0xFF))
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(0xFFD2, mpu.pc)
        self.assertEqual(0x1FD,   mpu.sp)
        self.assertEqual(0xC0,   mpu.memory[0x01FF])  # PCH
        self.assertEqual(0x02,   mpu.memory[0x01FE])  # PCL+2

    # RTI

    def test_rti_restores_status_and_pc_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 RTI
        mpu.memory[0x0000] = 0x40
        self._write(mpu.memory, 0x01FC, (0xFC, 0x03, 0xC0, 0x00))  # Status, PCL, PCH, PBR
        mpu.sp = 0x1FB

        mpu.step()
        self.assertEqual(0xC003, mpu.pc)
        self.assertEqual(0xFC,   mpu.p)
        self.assertEqual(0x1FF,   mpu.sp)
        self.assertEqual(0,   mpu.pbr)

    def test_rti_8_to_16_bit_affects_registers(self):
        mpu = self._make_mpu()
        mpu.a = 0x34
        mpu.b = 0x12
        mpu.x = 0x34
        mpu.y = 0x34
        mpu.sp = 0x01FB
        self.assertEqual(mpu.MS, mpu.p & mpu.MS)
        self.assertEqual(mpu.IRS, mpu.p & mpu.IRS)
        # $0000 RTI
        mpu.memory[0x0000] = 0x40
        self._write(mpu.memory, 0x01FC, (0x8A, 0x03, 0xC0, 0x00))  # Status, PCL, PCH
        mpu.step()
        self.assertEqual(0xC003, mpu.pc)
        self.assertEqual(0x1234, mpu.a)
        self.assertEqual(0, mpu.b)
        self.assertEqual(0x34, mpu.x)
        self.assertEqual(0x34, mpu.y)
        self.assertEqual(0, mpu.p & mpu.MS)
        self.assertEqual(0, mpu.p & mpu.IRS)
        self.assertEqual(0x8A, mpu.p)
        self.assertEqual(0x1FF, mpu.sp)
        self.assertEqual(0,   mpu.pbr)

    # PHA

    def test_pha_pushes_a_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.a = 0xAB
        # $0000 PHA
        mpu.memory[0x0000] = 0x48
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0x1FE, mpu.sp)

    # PHP

    def test_php_pushes_processor_status_and_updates_sp(self):
        for flags in range(0x100):
            mpu = self._make_mpu()
            mpu.p = flags | mpu.MS | mpu.IRS
            # $0000 PHP
            mpu.memory[0x0000] = 0x08
            mpu.step()
            self.assertEqual(0x0001, mpu.pc)
            self.assertEqual((flags | mpu.MS | mpu.IRS),
                             mpu.memory[0x1FF])
            self.assertEqual(0x1FE, mpu.sp)

    # PHX

    def test_phx_pushes_x_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.x = 0xAB
        # $0000 PHX
        mpu.memory[0x0000] = 0xDA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.x)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0x1FE, mpu.sp)
        self.assertEqual(3, mpu.processorCycles)

    # PHY

    def test_phy_pushes_y_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.y = 0xAB
        # $0000 PHY
        mpu.memory[0x0000] = 0x5A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.y)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0x1FE, mpu.sp)
        self.assertEqual(3, mpu.processorCycles)

    # PLA

    def test_pla_pulls_top_byte_from_stack_into_a_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLA
        mpu.memory[0x0000] = 0x68
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0x1FE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.a)
        self.assertEqual(0x1FF,   mpu.sp)

    # PLP


    def test_plp_pulls_top_byte_from_stack_into_flags_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLP
        mpu.memory[0x0000] = 0x28
        mpu.memory[0x01FF] = 0xBA
        mpu.sp = 0x1FE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xBA, mpu.p)
        self.assertEqual(0x1FF, mpu.sp)

    def test_plp_8_to_16_bit_affects_registers(self):
        mpu = self._make_mpu()
        mpu.a = 0x34
        mpu.b = 0x12
        mpu.x = 0x34
        mpu.y = 0x34
        mpu.sp = 0x1FE
        mpu.memory[0x01FF] = 0x8A
        self.assertEqual(mpu.MS, mpu.p & mpu.MS)
        self.assertEqual(mpu.IRS, mpu.p & mpu.IRS)
        # $0000 PLP
        mpu.memory[0x0000] = 0x28
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x1234, mpu.a)
        self.assertEqual(0, mpu.b)
        self.assertEqual(0x34, mpu.x)
        self.assertEqual(0x34, mpu.y)
        self.assertEqual(0, mpu.p & mpu.MS)
        self.assertEqual(0, mpu.p & mpu.IRS)
        self.assertEqual(0x8A, mpu.p)
        self.assertEqual(0x1FF, mpu.sp)

    # PLX

    def test_plx_pulls_top_byte_from_stack_into_x_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLX
        mpu.memory[0x0000] = 0xFA
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0x1FE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.x)
        self.assertEqual(0x1FF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # PLY

    def test_ply_pulls_top_byte_from_stack_into_y_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLY
        mpu.memory[0x0000] = 0x7A
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0x1FE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.y)
        self.assertEqual(0x1FF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # REP

    def test_rep_8_to_16_bit_affects_registers(self):
        mpu = self._make_mpu()
        mpu.a = 0x34
        mpu.b = 0x12
        mpu.x = 0x34
        mpu.y = 0x34
        self.assertEqual(mpu.MS, mpu.p & mpu.MS)
        self.assertEqual(mpu.IRS, mpu.p & mpu.IRS)
        # $0000 REP #$30
        self._write(mpu.memory, 0x0000, (0xC2, 0x30))
        mpu.step()
        self.assertEqual(0x1234, mpu.a)
        self.assertEqual(0, mpu.b)
        self.assertEqual(0x34, mpu.x)
        self.assertEqual(0x34, mpu.y)
        self.assertEqual(0, mpu.p & mpu.MS)
        self.assertEqual(0, mpu.p & mpu.IRS)

    # RTS

    def test_rts_restores_pc_and_increments_then_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 RTS
        mpu.memory[0x0000] = 0x60
        self._write(mpu.memory, 0x01FE, (0x03, 0xC0))  # PCL, PCH
        mpu.pc = 0x0000
        mpu.sp = 0x1FD

        mpu.step()
        self.assertEqual(0xC004, mpu.pc)
        self.assertEqual(0x1FF,   mpu.sp)

    def test_rts_wraps_around_top_of_memory(self):
        mpu = self._make_mpu()
        # $1000 RTS
        mpu.memory[0x1000] = 0x60
        self._write(mpu.memory, 0x01FE, (0xFF, 0xFF))  # PCL, PCH
        mpu.pc = 0x1000
        mpu.sp = 0x1FD

        mpu.step()
        self.assertEqual(0x0000, mpu.pc)
        self.assertEqual(0x1FF,   mpu.sp)

    # TCD

    def test_tcd_transfers_accumulator_into_d(self):
        mpu = self._make_mpu()
        mpu.a = 0xCD
        mpu.b = 0xAB
        # $0000 TCD
        mpu.memory[0x0000] = 0x5B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xCD, mpu.a)
        self.assertEqual(0xAB, mpu.b)
        self.assertEqual(0xABCD, mpu.dpr)

    def test_tcd_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x000
        mpu.b = 0x80
        # $0000 TCD
        mpu.memory[0x0000] = 0x5B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x80, mpu.b)
        self.assertEqual(0x8000, mpu.dpr)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tcd_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.b = 0x00
        # $0000 TCD
        mpu.memory[0x0000] = 0x5B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.b)
        self.assertEqual(0x00, mpu.dpr)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TCS

    def test_tcs_transfers_accumulator_into_s(self):
        mpu = self._make_mpu()
        mpu.b = 0xAB
        mpu.a = 0xCD
        # $0000 TCS
        mpu.memory[0x0000] = 0x1B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xCD, mpu.a)
        self.assertEqual(0xABCD, mpu.sp)

    def test_tcs_does_not_set_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x80
        # $0000 TCS
        mpu.memory[0x0000] = 0x1B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0x80, mpu.sp)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_tcs_does_not_set_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 TCS
        mpu.memory[0x0000] = 0x1B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.sp)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # TDC

    def test_tdc_transfers_d_to_accumulator(self):
        mpu = self._make_mpu()
        mpu.dpr = 0xABCD
        # $0000 TDC
        mpu.memory[0x0000] = 0x7B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xCD, mpu.a)
        self.assertEqual(0xAB, mpu.b)
        self.assertEqual(0xABCD, mpu.dpr)

    def test_tdc_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.dpr = 0x8000
        # $0000 TDC
        mpu.memory[0x0000] = 0x7B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x80, mpu.b)
        self.assertEqual(0x8000, mpu.dpr)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tdc_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.dpr = 0x00
        # $0000 TDC
        mpu.memory[0x0000] = 0x7B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.b)
        self.assertEqual(0x00, mpu.dpr)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TSC

    def test_tsc_transfers_accumulator_into_s(self):
        mpu = self._make_mpu()
        mpu.sp = 0xABCD
        # $0000 TSC
        mpu.memory[0x0000] = 0x3B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xCD, mpu.a)
        self.assertEqual(0xAB, mpu.b)
        self.assertEqual(0xABCD, mpu.sp)

    def test_tsc_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.sp = 0x8000
        # $0000 TSC
        mpu.memory[0x0000] = 0x3B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x80, mpu.b)
        self.assertEqual(0x8000, mpu.sp)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tsc_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.sp = 0x00
        # $0000 TSC
        mpu.memory[0x0000] = 0x3B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.b)
        self.assertEqual(0x00, mpu.sp)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TSX

    def test_tsx_transfers_stack_pointer_lsb_into_x(self):
        mpu = self._make_mpu()
        mpu.sp = 0xABCD
        mpu.x = 0x00
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.sp)
        self.assertEqual(0xCD, mpu.x)

    # TXY

    def test_txy_transfers_x_into_y(self):
        mpu = self._make_mpu()
        mpu.x = 0xAB
        mpu.y = 0x00
        # $0000 TXY
        mpu.memory[0x0000] = 0x9B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.y)
        self.assertEqual(0xAB, mpu.x)

    def test_txy_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x80
        mpu.y = 0x00
        # $0000 TXY
        mpu.memory[0x0000] = 0x9B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_txy_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x00
        mpu.y = 0xFF
        # $0000 TXY
        mpu.memory[0x0000] = 0x9B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TXS

    def test_txs_transfers_x_into_stack_pointer_msb_zero(self):
        mpu = self._make_mpu()
        mpu.sp = 0xABCD
        mpu.x = 0xCD
        # $0000 TXS
        mpu.memory[0x0000] = 0x9A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xCD, mpu.sp)
        self.assertEqual(0xCD, mpu.x)

    # TYX

    def test_tyx_transfers_y_into_x(self):
        mpu = self._make_mpu()
        mpu.y = 0xAB
        mpu.x = 0x00
        # $0000 TYX
        mpu.memory[0x0000] = 0xBB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.y)
        self.assertEqual(0xAB, mpu.x)

    def test_tyx_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.y = 0x80
        mpu.x = 0x00
        # $0000 TYX
        mpu.memory[0x0000] = 0xBB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tyx_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.y = 0x00
        mpu.x = 0xFF
        # $0000 TYX
        mpu.memory[0x0000] = 0xBB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # XBA

    def test_xba_exchanges_b_and_a(self):
        mpu = self._make_mpu()
        mpu.b = 0xAB
        mpu.a = 0xCD
        # $0000 XBA
        mpu.memory[0x0000] = 0xEB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xCD, mpu.b)
        self.assertEqual(0xAB, mpu.a)

    def test_xba_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x80
        mpu.b = 0x00
        # $0000 XBA
        mpu.memory[0x0000] = 0xEB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.b)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_xba_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.b = 0xFF
        mpu.a = 0x00
        # $0000 XBA
        mpu.memory[0x0000] = 0xEB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0x00, mpu.b)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # XCE

    def test_xce_exchange_c_and_e_bits(self):
        mpu = self._make_mpu() # native mode, carry is cleared

        mpu.pSET(mpu.CARRY)

        mpu.memory[0x0000] = 0xFB
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(mpu.MS, mpu.p & mpu.MS)
        self.assertEqual(mpu.IRS, mpu.p & mpu.IRS)
        self.assertEqual(1, mpu.mode)

    def test_xce_forces_a_to_8_bits(self):
        mpu = self._make_mpu() # native mode, carry is cleared

        mpu.a = 0xabcd
        mpu.pSET(mpu.CARRY)

        mpu.memory[0x0000] = 0xFB
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(1, mpu.mode)
        self.assertEqual(0xcd, mpu.a)
        self.assertEqual(0xab, mpu.b)



    def test_make_mpu(self):
        # test that we haven't changed key make_mpu assumptions
        # _make_mpu should:
        #   * set native mode
        #   * set 8 bit registers
        #   * clear carry
        #   * set sp to 0x1ff
        #   * set memory to 0x30000 * [0xAA]
        mpu = self._make_mpu()
        self.assertEqual(0, mpu.mode)
        self.assertEqual(mpu.MS, mpu.p & mpu.MS)
        self.assertEqual(mpu.IRS, mpu.p & mpu.IRS)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0x1ff, mpu.sp)
        for addr in range(0x30000):
            self.assertEqual(0xAA, mpu.memory[addr])

    # Test Helpers

    def _make_mpu(self, *args, **kargs):
        klass = self._get_target_class()
        mpu = klass(*args, **kargs)
        if 'memory' not in kargs:
            mpu.memory = 0x30000 * [0xAA]

        # set native mode
        mpu.pCLR(mpu.CARRY)
        mpu.inst_0xfb() # XCE
        mpu.pCLR(mpu.CARRY) # many 6502 based tests expect the carry flag to be clear

        # py65 mpus have sp set to $ff, I've modeled the 65816
        # based on the physical chip which requires sp to be set
        # in software.  The core tests assume sp is set to $ff,
        # so we have to set sp here
        mpu.sp = 0x1ff 
        
        return mpu

    def _write(self, memory, start_address, bytes):
        memory[start_address:start_address + len(bytes)] = bytes

    def _get_target_class(self):
        return MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
