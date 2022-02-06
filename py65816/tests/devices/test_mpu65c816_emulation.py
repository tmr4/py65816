import unittest # python -m unittest discover -p "*816_emulation.py"
import sys
from py65816.devices.mpu65c816 import MPU
from py65816.tests.devices.mpu65816_Common_tests_6502 import Common6502Tests
from py65816.tests.devices.mpu65816_Common_tests_65c02 import Common65C02Tests

# x tests
class MPUTests(unittest.TestCase, Common6502Tests, Common65C02Tests):
#class MPUTests(unittest.TestCase):
    """CMOS 65C816 Tests - Emulation Mode """

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertTrue('65C816' in repr(mpu))

    # Emulation Mode

    # Page Bounday Wrap Tests
    def test_dpx_wraps_at_page_boundary_when_dl_zero(self):
        mpu = self._make_mpu()
        mpu.dpr = 0x0100
        mpu.x = 1
        self._write(mpu.memory, 0x00ff, (0x34, 0x12))
        self._write(mpu.memory, 0x01ff, (0xcd, 0xab))
        # $0000 LDA $ff,X
        self._write(mpu.memory, 0x0000, (0xb5, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x12, mpu.a)

    def test_dpi_wraps_page_boundary_when_dl_zero(self):
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
        self.assertEqual(0x10, mpu.a)

    def test_dix_wraps_page_boundary_when_dl_zero(self):
        mpu = self._make_mpu()
        mpu.dpr = 0x0100
        mpu.x = 1
        self._write(mpu.memory, 0x0100, (0xcd, 0xab))
        self._write(mpu.memory, 0x01ff, (0x34, 0x12))
        self._write(mpu.memory, 0x1234, (0x78, 0x56))
        self._write(mpu.memory, 0xabcd, (0xbc, 0x9a))
        self._write(mpu.memory, 0xcd34, (0x10, 0x20))
        # $0000 LDA ($ff,X)
        self._write(mpu.memory, 0x0000, (0xa1, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xbc, mpu.a)

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

    def test_stack_wrap_at_page_boundary(self):
        mpu = self._make_mpu()
        mpu.sp = 0x01ff
        self._write(mpu.memory, 0x00ff, (0x34, 0x12))
        self._write(mpu.memory, 0x01ff, (0xcd, 0xab))
        # $000 PLA
        mpu.memory[0x0000] = 0x68
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x12, mpu.a)

    def test_no_wrap_at_page_boundary_new_addr_mode_str(self):
        mpu = self._make_mpu()
        mpu.sp = 0x0101
        self._write(mpu.memory, 0x00ff, (0x34, 0x12))
        self._write(mpu.memory, 0x01ff, (0xcd, 0xab))
        # $0000 LDA $ff,S
        self._write(mpu.memory, 0x0000, (0xa3, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xab, mpu.a)

    def test_no_wrap_at_page_boundary_new_inst_pei(self):
        mpu = self._make_mpu()
        mpu.dpr = 0x0300
        mpu.sp = 0xff
        self._write(mpu.memory, 0x02ff, (0x34, 0x12))
        self._write(mpu.memory, 0x03ff, (0xcd, 0xab, 0xff))
        # $000 PEI $ff
        self._write(mpu.memory, 0x0000, (0xd4, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xfd, mpu.sp)
        self.assertEqual(0xab, mpu.memory[0x01ff])
        self.assertEqual(0xcd, mpu.memory[0x01fe])

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

    # in emulation mode the stack pointer is confined to page 1 and thus can't
    # wrap at the bank 0 boundary

    def test_jmp_abi_operand_deref_wraps_at_bank_zero_boundary(self):
        mpu = self._make_mpu()
        # $0100 JMP ($ffff)
        mpu.pc = 0x0100
        self._write(mpu.memory, 0x0100, (0x6C, 0xff, 0xff))
        self._write(mpu.memory, 0xffff, (0x34, 0x12))
        mpu.memory[0x0000] = 0xab
        mpu.step()
        self.assertEqual(0xab34, mpu.pc)
        self.assertEqual(0x00, mpu.pbr)

    def test_jmp_ail_wraps_at_bank_zero_boundary(self):
        mpu = self._make_mpu()
        # $0100 JMP [$ffff]
        mpu.pc = 0x0100
        self._write(mpu.memory, 0x0100, (0xDC, 0xff, 0xff))
        self._write(mpu.memory, 0xffff, (0x34, 0x12, 0x01))
        self._write(mpu.memory, 0x0000, (0xab, 0x01))
        mpu.step()
        self.assertEqual(0xab34, mpu.pc)
        self.assertEqual(0x01, mpu.pbr)

    def test_jmp_ail_wraps_at_bank_zero_boundary_2(self):
        mpu = self._make_mpu()
        # $0100 JMP [$fffe]
        mpu.pc = 0x0100
        self._write(mpu.memory, 0x0100, (0xDC, 0xfe, 0xff))
        self._write(mpu.memory, 0xfffe, (0x34, 0x12, 0x01))
        self._write(mpu.memory, 0x0000, (0x01, 0x02))
        mpu.step()
        self.assertEqual(0x1234, mpu.pc)
        self.assertEqual(0x01, mpu.pbr)

    def test_jmp_aix_wraps_at_bank_k_boundary(self):
        mpu = self._make_mpu()
        mpu.x = 0xff
        mpu.pbr = 0x01
        mpu.pc = 0x0100
        # $010100 JMP ($ff00,X)
        self._write(mpu.memory, 0x010100, (0x7C, 0x00, 0xff))
        self._write(mpu.memory, 0x01ffff, (0x34, 0x12))
        self._write(mpu.memory, 0x010000, (0xab, 0x01))
        mpu.step()
        self.assertEqual(0xab34, mpu.pc)
        self.assertEqual(0x01, mpu.pbr)


    # Reset

    def test_make_mpu(self):
        # test that we haven't changed key make_mpu assumptions
        # _make_mpu should:
        #   * begin in reset state
        #   * set sp to 0xff
        #   * set memory to 0x10000 * [0xAA]
        mpu = self._make_mpu()
        self.assertEqual(1, mpu.mode)
        self.assertEqual(mpu.BREAK | mpu.UNUSED | mpu.INTERRUPT, mpu.p)
        self.assertEqual(0xff, mpu.sp)
        for addr in range(0x10000):
            self.assertEqual(0xAA, mpu.memory[addr])

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
        self.assertEqual(mpu.BREAK, mpu.p & mpu.BREAK)
        self.assertEqual(0, mpu.p & mpu.DECIMAL)

    def test_brk_interrupt(self):
        mpu = self._make_mpu()
        mpu.p = 0x60 # bits 4 and 5 always set in emulation mode
        self._write(mpu.memory, 0xFFFE, (0x00, 0x04))

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
        mpu.p = mpu.BREAK | mpu.UNUSED
        self._write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
        # $C000 BRK
        mpu.memory[0xC000] = 0x00
        mpu.pc = 0xC000
        p = mpu.p | mpu.BREAK
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

        self.assertEqual(0xC0, mpu.memory[0x1FF])  # PCH
        self.assertEqual(0x02, mpu.memory[0x1FE])  # PCL
        self.assertEqual(p | mpu.BREAK | mpu.UNUSED, mpu.memory[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.sp)

        self.assertEqual(mpu.BREAK | mpu.UNUSED | mpu.INTERRUPT, mpu.p)

    # IRQ and NMI handling (very similar to BRK)

    def test_irq_pushes_pc_and_correct_status_then_sets_pc_to_irq_vector(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.INTERRUPT # enable interrupts
        self._write(mpu.memory, 0xFFFA, (0x88, 0x77))
        self._write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
        mpu.pc = 0xC123
        p = mpu.p
        mpu.irq()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(0xC1, mpu.memory[0x1FF])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FE])  # PCL
        self.assertEqual(p & ~mpu.BREAK, mpu.memory[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.sp)
        self.assertEqual(mpu.BREAK | mpu.UNUSED | mpu.INTERRUPT, mpu.p)
        self.assertEqual(7, mpu.processorCycles)

    def test_nmi_pushes_pc_and_correct_status_then_sets_pc_to_nmi_vector(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFFFA, (0x88, 0x77))
        self._write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
        mpu.pc = 0xC123
        p = mpu.p
        mpu.nmi()
        self.assertEqual(0x7788, mpu.pc)
        self.assertEqual(0xC1, mpu.memory[0x1FF])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FE])  # PCL
        self.assertEqual(p & ~mpu.BREAK, mpu.memory[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.sp)
        self.assertEqual(mpu.BREAK | mpu.UNUSED | mpu.INTERRUPT, mpu.p)
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
        self.assertEqual(0xFD,   mpu.sp)
        self.assertEqual(0xC0,   mpu.memory[0x01FF])  # PCH
        self.assertEqual(0x02,   mpu.memory[0x01FE])  # PCL+2

    # RTI

    def test_rti_break_and_unused_flags_stay_high(self):
        mpu = self._make_mpu()
        # $0000 RTI
        mpu.memory[0x0000] = 0x40
        self._write(mpu.memory, 0x01FD, (0x00, 0x03, 0xC0))  # Status, PCL, PCH
        mpu.sp = 0xFC

        mpu.step()
        self.assertEqual(mpu.BREAK, mpu.p & mpu.BREAK)
        self.assertEqual(mpu.UNUSED, mpu.p & mpu.UNUSED)

    def test_rti_restores_status_and_pc_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 RTI
        mpu.memory[0x0000] = 0x40
        self._write(mpu.memory, 0x01FD, (0xFC, 0x03, 0xC0))  # Status, PCL, PCH
        mpu.sp = 0xFC

        mpu.step()
        self.assertEqual(0xC003, mpu.pc)
        self.assertEqual(0xFC,   mpu.p)
        self.assertEqual(0xFF,   mpu.sp)

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
        self.assertEqual(0xFE, mpu.sp)

    # PHP

    def test_php_pushes_processor_status_and_updates_sp(self):
        for flags in range(0x100):
            mpu = self._make_mpu()
            mpu.p = flags | mpu.BREAK | mpu.UNUSED
            # $0000 PHP
            mpu.memory[0x0000] = 0x08
            mpu.step()
            self.assertEqual(0x0001, mpu.pc)
            self.assertEqual((flags | mpu.BREAK | mpu.UNUSED),
                             mpu.memory[0x1FF])
            self.assertEqual(0xFE, mpu.sp)

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
        self.assertEqual(0xFE, mpu.sp)
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
        self.assertEqual(0xFE, mpu.sp)
        self.assertEqual(3, mpu.processorCycles)

    # PLA

    def test_pla_pulls_top_byte_from_stack_into_a_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLA
        mpu.memory[0x0000] = 0x68
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.a)
        self.assertEqual(0xFF,   mpu.sp)

    # PLP

    def test_plp_pulls_top_byte_from_stack_into_flags_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLP
        mpu.memory[0x0000] = 0x28
        mpu.memory[0x01FF] = 0xBA  # must have BREAK and UNUSED set
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xBA,   mpu.p)
        self.assertEqual(0xFF,   mpu.sp)

    # PLX

    def test_plx_pulls_top_byte_from_stack_into_x_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLX
        mpu.memory[0x0000] = 0xFA
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.x)
        self.assertEqual(0xFF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # PLY

    def test_ply_pulls_top_byte_from_stack_into_y_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLY
        mpu.memory[0x0000] = 0x7A
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.y)
        self.assertEqual(0xFF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # REP

    def test_rep_cannot_reset_bit_4_or_5(self):
        mpu = self._make_mpu()
        # $0000 REP #$30
        self._write(mpu.memory, 0x0000, (0xC2, 0x30))
        mpu.step()
        self.assertEqual(mpu.MS, mpu.p & mpu.MS)
        self.assertEqual(mpu.IRS, mpu.p & mpu.IRS)

    def test_rep_can_reset_other_bits(self):
        mpu = self._make_mpu()
        mpu.p = 0xFF
        # $0000 REP #$CF
        self._write(mpu.memory, 0x0000, (0xC2, 0xCF))
        mpu.step()
        self.assertEqual(0x30, mpu.p)

    # RTS

    def test_rts_restores_pc_and_increments_then_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 RTS
        mpu.memory[0x0000] = 0x60
        self._write(mpu.memory, 0x01FE, (0x03, 0xC0))  # PCL, PCH
        mpu.pc = 0x0000
        mpu.sp = 0xFD

        mpu.step()
        self.assertEqual(0xC004, mpu.pc)
        self.assertEqual(0xFF,   mpu.sp)

    def test_rts_wraps_around_top_of_memory(self):
        mpu = self._make_mpu()
        # $1000 RTS
        mpu.memory[0x1000] = 0x60
        self._write(mpu.memory, 0x01FE, (0xFF, 0xFF))  # PCL, PCH
        mpu.pc = 0x1000
        mpu.sp = 0xFD

        mpu.step()
        self.assertEqual(0x0000, mpu.pc)
        self.assertEqual(0xFF,   mpu.sp)

    # SEP

    #def test_sep_cannot_set_bit_4_or_5(self):
    #    mpu = self._make_mpu()
    #    # $0000 REP #$30
    #    self._write(mpu.memory, 0x0000, (0xE2, 0x30))
    #    mpu.step()
    #    self.assertEqual(mpu.MS, mpu.p & mpu.MS)
    #    self.assertEqual(mpu.IRS, mpu.p & mpu.IRS)

    def test_sep_can_set_other_bits(self):
        mpu = self._make_mpu()
        mpu.p = 0x30
        # $0000 SEP #$CF
        self._write(mpu.memory, 0x0000, (0xE2, 0xCF))
        mpu.step()
        self.assertEqual(0xff, mpu.p)

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
        self.assertEqual(0xCD, mpu.sp)

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

    # TSC

    def test_tsc_transfers_accumulator_into_s(self):
        mpu = self._make_mpu()
        mpu.sp = 0xABCD
        # $0000 TSC
        mpu.memory[0x0000] = 0x3B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xCD, mpu.a)
        self.assertEqual(0x01, mpu.b)
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
        self.assertEqual(0x01, mpu.b)
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
        self.assertEqual(0x01, mpu.b)
        self.assertEqual(0x00, mpu.sp)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # XCE

    def test_xce_exchange_c_and_e_bits(self):
        mpu = self._make_mpu() # emulation mode, carry is cleared

        mpu.memory[0x0000] = 0xFB
        mpu.step()
        self.assertEqual(1, mpu.p & mpu.CARRY)
        self.assertEqual(mpu.MS, mpu.p & mpu.MS)
        self.assertEqual(mpu.IRS, mpu.p & mpu.IRS)
        self.assertEqual(0, mpu.mode)

    # *** TODO: need to verify what happens on hardware ***
#    def test_xce_forces_registers_to_8_bits(self):
#        mpu = self._make_mpu() # emulation mode, carry is cleared
#
#        mpu.a = 0xabcd
#        mpu.x = 0xabcd
#        mpu.y = 0xabcd
#
#        mpu.memory[0x0000] = 0xFB
#        mpu.step()
#        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
#        self.assertEqual(0, mpu.mode)
#
#        self.assertEqual(0xcd, mpu.a)
#        self.assertEqual(0xcd, mpu.x)
#        self.assertEqual(0xcd, mpu.y)
#        self.assertEqual(0, mpu.b)



    # Test Helpers

    def _make_mpu(self, *args, **kargs):
        klass = self._get_target_class()
        mpu = klass(*args, **kargs)
        if 'memory' not in kargs:
            mpu.memory = 0x30000 * [0xAA]

        # py65 mpus have sp set to $ff, I've modeled the 65816
        # based on the physical chip which requires sp to be set
        # in software.  The core tests assume sp is set to $ff,
        # so we have to set sp here
        mpu.sp = 0xff 
        
        return mpu

    def _write(self, memory, start_address, bytes):
        memory[start_address:start_address + len(bytes)] = bytes

    def _get_target_class(self):
        return MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
