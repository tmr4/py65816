# from test_mpu6502.py, 434 tests

class Common65816NativeTests:
    """Tests common to 65816-based microprocessors Running in Native Mode"""

    # Reset

    def test_reset_sets_registers_to_initial_states(self):
        mpu = self._make_mpu()
        mpu.reset()
        #self.assertEqual(0xFF, mpu.sp)
        self.assertEqual(0, mpu.a)
        self.assertEqual(0, mpu.x)
        self.assertEqual(0, mpu.y)
        self.assertEqual(mpu.MS | mpu.IRS, mpu.p)

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
        #mpu.p = 0x60 # bits 4 and 5 always set in emulation mode
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
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

        self.assertEqual(0x00, mpu.memory[0x1FF])  # PBR
        self.assertEqual(0xC0, mpu.memory[0x1FE])  # PCH
        self.assertEqual(0x02, mpu.memory[0x1FD])  # PCL
        self.assertEqual(mpu.MS | mpu.IRS, mpu.memory[0x1FC])  # Status
        self.assertEqual(0x1FB, mpu.sp)

        self.assertEqual(mpu.MS | mpu.IRS | mpu.INTERRUPT, mpu.p)

    # IRQ and NMI handling (very similar to BRK)

    def test_irq_pushes_pc_and_correct_status_then_sets_pc_to_irq_vector(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFFEA, (0x88, 0x77))
        self._write(mpu.memory, 0xFFEE, (0xCD, 0xAB))
        mpu.pc = 0xC123
        mpu.irq()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x1FF])  # PBR
        self.assertEqual(0xC1, mpu.memory[0x1FE])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FD])  # PCL
        self.assertEqual(mpu.MS | mpu.IRS, mpu.memory[0x1FC])  # Status
        self.assertEqual(0x1FB, mpu.sp)
        self.assertEqual(mpu.MS | mpu.IRS | mpu.INTERRUPT, mpu.p)
        self.assertEqual(7, mpu.processorCycles)

    def test_nmi_pushes_pc_and_correct_status_then_sets_pc_to_nmi_vector(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFFEA, (0x88, 0x77))
        self._write(mpu.memory, 0xFFEE, (0xCD, 0xAB))
        mpu.pc = 0xC123
        mpu.nmi()
        self.assertEqual(0x7788, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x1FF])  # PBR
        self.assertEqual(0xC1, mpu.memory[0x1FE])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FD])  # PCL
        self.assertEqual(mpu.MS | mpu.IRS, mpu.memory[0x1FC])  # Status
        self.assertEqual(0x1FB, mpu.sp)
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
        mpu.memory[0x01FF] = 0xBA  # must have BREAK and UNUSED set
        mpu.sp = 0x1FE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xBA,   mpu.p)
        self.assertEqual(0x1FF,   mpu.sp)

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

    # ADC Immediate

    def test_adc_bcd_on_immediate_79_plus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x79
        # $0000 ADC #$00
        self._write(mpu.memory, 0x0000, (0x69, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_adc_bcd_on_immediate_6f_plus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x6f
        # $0000 ADC #$00
        self._write(mpu.memory, 0x0000, (0x69, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x76, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_adc_bcd_on_immediate_9c_plus_9d(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x9c
        # $0000 ADC #$9d
        # $0002 ADC #$9d
        self._write(mpu.memory, 0x0000, (0x69, 0x9d))
        self._write(mpu.memory, 0x0002, (0x69, 0x9d))
        mpu.step()
        self.assertEqual(0x9f, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x93, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # BCC

    def test_bcc_carry_clear_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 BCC +6
        self._write(mpu.memory, 0x0000, (0x90, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bcc_carry_clear_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0000 BCC -6
        self._write(mpu.memory, 0x0050, (0x90, rel))
        mpu.step()
        self.assertEqual(0x0052 - 0x06, mpu.pc)

    def test_bcc_carry_set_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 BCC +6
        self._write(mpu.memory, 0x0000, (0x90, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BCS

    def test_bcs_carry_set_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 BCS +6
        self._write(mpu.memory, 0x0000, (0xB0, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bcs_carry_set_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0000 BCS -6
        self._write(mpu.memory, 0x0050, (0xB0, rel))
        mpu.step()
        self.assertEqual(0x0052 - 0x06, mpu.pc)

    def test_bcs_carry_clear_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 BCS +6
        self._write(mpu.memory, 0x0000, (0xB0, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BEQ

    def test_beq_zero_set_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BEQ +6
        self._write(mpu.memory, 0x0000, (0xF0, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_beq_zero_set_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0000 BEQ -6
        self._write(mpu.memory, 0x0050, (0xF0, rel))
        mpu.step()
        self.assertEqual(0x0052 - 0x06, mpu.pc)

    def test_beq_zero_clear_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BEQ +6
        self._write(mpu.memory, 0x0000, (0xF0, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BMI

    def test_bmi_negative_set_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BMI +06
        self._write(mpu.memory, 0x0000, (0x30, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bmi_negative_set_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        mpu.pc = 0x0050
        # $0000 BMI -6
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        self._write(mpu.memory, 0x0050, (0x30, rel))
        mpu.step()
        self.assertEqual(0x0052 - 0x06, mpu.pc)

    def test_bmi_negative_clear_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BEQ +6
        self._write(mpu.memory, 0x0000, (0x30, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BNE

    def test_bne_zero_clear_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BNE +6
        self._write(mpu.memory, 0x0000, (0xD0, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bne_zero_clear_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.pc = 0x0050
        # $0050 BNE -6
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        self._write(mpu.memory, 0x0050, (0xD0, rel))
        mpu.step()
        self.assertEqual(0x0052 - 0x06, mpu.pc)

    def test_bne_zero_set_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BNE +6
        self._write(mpu.memory, 0x0000, (0xD0, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BPL

    def test_bpl_negative_clear_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BPL +06
        self._write(mpu.memory, 0x0000, (0x10, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bpl_negative_clear_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.pc = 0x0050
        # $0050 BPL -6
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        self._write(mpu.memory, 0x0050, (0x10, rel))
        mpu.step()
        self.assertEqual(0x0052 - 0x06, mpu.pc)

    def test_bpl_negative_set_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BPL +6
        self._write(mpu.memory, 0x0000, (0x10, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BVC

    def test_bvc_overflow_clear_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BVC +6
        self._write(mpu.memory, 0x0000, (0x50, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bvc_overflow_clear_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0050 BVC -6
        self._write(mpu.memory, 0x0050, (0x50, rel))
        mpu.step()
        self.assertEqual(0x0052 - 0x06, mpu.pc)

    def test_bvc_overflow_set_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BVC +6
        self._write(mpu.memory, 0x0000, (0x50, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BVS

    def test_bvs_overflow_set_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BVS +6
        self._write(mpu.memory, 0x0000, (0x70, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bvs_overflow_set_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF) + 1  # two's complement of 6
        # $0050 BVS -6
        self._write(mpu.memory, 0x0050, (0x70, rel))
        mpu.step()
        self.assertEqual(0x0052 - 0x06, mpu.pc)

    def test_bvs_overflow_clear_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BVS +6
        self._write(mpu.memory, 0x0000, (0x70, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # CLC

    def test_clc_clears_carry_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 CLC
        mpu.memory[0x0000] = 0x18
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    # CLD

    def test_cld_clears_decimal_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        # $0000 CLD
        mpu.memory[0x0000] = 0xD8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.DECIMAL)

    # CLI

    def test_cli_clears_interrupt_mask_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.INTERRUPT
        # $0000 CLI
        mpu.memory[0x0000] = 0x58
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.INTERRUPT)

    # CLV

    def test_clv_clears_overflow_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 CLV
        mpu.memory[0x0000] = 0xB8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)




    # INC Absolute

    def test_inc_abs_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x09
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0A, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Direct Page

    def test_inc_dp_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE6, 0x10))
        mpu.memory[0x0010] = 0x09
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0A, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_dp_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE6, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_dp_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE6, 0x10))
        mpu.memory[0x0010] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Absolute, X-Indexed

    def test_inc_abs_x_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.x = 0x03
        mpu.memory[0xABCD + mpu.x] = 0x09
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0A, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_x_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.x = 0x03
        mpu.memory[0xABCD + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_x_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.x = 0x03
        mpu.memory[0xABCD + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Direct Page, X-Indexed

    def test_inc_dp_x_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xF6, 0x10))
        mpu.x = 0x03
        mpu.memory[0x0010 + mpu.x] = 0x09
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0A, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_dp_x_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xF6, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_dp_x_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xF6, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INX

    def test_inx_increments_x(self):
        mpu = self._make_mpu()
        mpu.x = 0x09
        mpu.memory[0x0000] = 0xE8  # => INX
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0A, mpu.x)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inx_above_FF_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        mpu.memory[0x0000] = 0xE8  # => INX
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_inx_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        mpu.x = 0x7f
        mpu.memory[0x0000] = 0xE8  # => INX
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INY

    def test_iny_increments_y(self):
        mpu = self._make_mpu()
        mpu.y = 0x09
        mpu.memory[0x0000] = 0xC8  # => INY
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0A, mpu.y)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_iny_above_FF_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        mpu.memory[0x0000] = 0xC8  # => INY
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_iny_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        mpu.y = 0x7f
        mpu.memory[0x0000] = 0xC8  # => INY
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # JMP Absolute

    def test_jmp_abs_jumps_to_absolute_address(self):
        mpu = self._make_mpu()
        # $0000 JMP $ABCD
        self._write(mpu.memory, 0x0000, (0x4C, 0xCD, 0xAB))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

    # JMP Indirect

    def test_jmp_ind_jumps_to_indirect_address(self):
        mpu = self._make_mpu()
        # $0000 JMP ($ABCD)
        self._write(mpu.memory, 0x0000, (0x6C, 0x00, 0x02))
        self._write(mpu.memory, 0x0200, (0xCD, 0xAB))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

    # LDA Absolute

    def test_lda_absolute_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA $ABCD
        self._write(mpu.memory, 0x0000, (0xAD, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_absolute_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 LDA $ABCD
        self._write(mpu.memory, 0x0000, (0xAD, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Direct Page

    def test_lda_dp_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA $0010
        self._write(mpu.memory, 0x0000, (0xA5, 0x10))
        mpu.memory[0x0010] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_dp_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 LDA $0010
        self._write(mpu.memory, 0x0000, (0xA5, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Immediate

    def test_lda_immediate_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA #$80
        self._write(mpu.memory, 0x0000, (0xA9, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_immediate_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 LDA #$00
        self._write(mpu.memory, 0x0000, (0xA9, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Absolute, X-Indexed

    def test_lda_abs_x_indexed_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 LDA $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBD, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_abs_x_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 LDA $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBD, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lda_abs_x_indexed_does_not_page_wrap(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0xFF
        # $0000 LDA $0080,X
        self._write(mpu.memory, 0x0000, (0xBD, 0x80, 0x00))
        mpu.memory[0x0080 + mpu.x] = 0x42
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x42, mpu.a)

    # LDA Absolute, Y-Indexed

    def test_lda_abs_y_indexed_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 LDA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xB9, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_abs_y_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 LDA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xB9, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lda_abs_y_indexed_does_not_page_wrap(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0xFF
        # $0000 LDA $0080,X
        self._write(mpu.memory, 0x0000, (0xB9, 0x80, 0x00))
        mpu.memory[0x0080 + mpu.y] = 0x42
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x42, mpu.a)

    # LDA Direct Page Indirect, Indexed (X)

    def test_lda_ind_indexed_x_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 LDA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xA1, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_ind_indexed_x_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 LDA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xA1, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Direct Page Indexed, Indirect (Y)

    def test_lda_indexed_ind_y_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB1, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_indexed_ind_y_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB1, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Direct Page, X-Indexed

    def test_lda_dp_x_indexed_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 LDA $10,X
        self._write(mpu.memory, 0x0000, (0xB5, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_dp_x_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 LDA $10,X
        self._write(mpu.memory, 0x0000, (0xB5, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Absolute

    def test_ldx_absolute_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        # $0000 LDX $ABCD
        self._write(mpu.memory, 0x0000, (0xAE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_absolute_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        # $0000 LDX $ABCD
        self._write(mpu.memory, 0x0000, (0xAE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Direct Page

    def test_ldx_dp_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        # $0000 LDX $0010
        self._write(mpu.memory, 0x0000, (0xA6, 0x10))
        mpu.memory[0x0010] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_dp_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        # $0000 LDX $0010
        self._write(mpu.memory, 0x0000, (0xA6, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Immediate

    def test_ldx_immediate_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        # $0000 LDX #$80
        self._write(mpu.memory, 0x0000, (0xA2, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_immediate_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        # $0000 LDX #$00
        self._write(mpu.memory, 0x0000, (0xA2, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Absolute, Y-Indexed

    def test_ldx_abs_y_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        mpu.y = 0x03
        # $0000 LDX $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xBE, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_abs_y_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        mpu.y = 0x03
        # $0000 LDX $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xBE, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Direct Page, Y-Indexed

    def test_ldx_dp_y_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        mpu.y = 0x03
        # $0000 LDX $0010,Y
        self._write(mpu.memory, 0x0000, (0xB6, 0x10))
        mpu.memory[0x0010 + mpu.y] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_dp_y_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        mpu.y = 0x03
        # $0000 LDX $0010,Y
        self._write(mpu.memory, 0x0000, (0xB6, 0x10))
        mpu.memory[0x0010 + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Absolute

    def test_ldy_absolute_loads_y_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        # $0000 LDY $ABCD
        self._write(mpu.memory, 0x0000, (0xAC, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_absolute_loads_y_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        # $0000 LDY $ABCD
        self._write(mpu.memory, 0x0000, (0xAC, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Direct Page

    def test_ldy_dp_loads_y_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        # $0000 LDY $0010
        self._write(mpu.memory, 0x0000, (0xA4, 0x10))
        mpu.memory[0x0010] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_dp_loads_y_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        # $0000 LDY $0010
        self._write(mpu.memory, 0x0000, (0xA4, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Immediate

    def test_ldy_immediate_loads_y_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        # $0000 LDY #$80
        self._write(mpu.memory, 0x0000, (0xA0, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_immediate_loads_y_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        # $0000 LDY #$00
        self._write(mpu.memory, 0x0000, (0xA0, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Absolute, X-Indexed

    def test_ldy_abs_x_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        mpu.x = 0x03
        # $0000 LDY $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBC, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_abs_x_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        mpu.x = 0x03
        # $0000 LDY $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBC, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Direct Page, X-Indexed

    def test_ldy_dp_x_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        mpu.x = 0x03
        # $0000 LDY $0010,X
        self._write(mpu.memory, 0x0000, (0xB4, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_dp_x_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        mpu.x = 0x03
        # $0000 LDY $0010,X
        self._write(mpu.memory, 0x0000, (0xB4, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Accumulator

    def test_lsr_accumulator_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR A
        mpu.memory[0x0000] = (0x4A)
        mpu.a = 0x00
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_accumulator_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        # $0000 LSR A
        mpu.memory[0x0000] = (0x4A)
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_accumulator_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR A
        mpu.memory[0x0000] = (0x4A)
        mpu.a = 0x04
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Absolute

    def test_lsr_absolute_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $ABCD
        self._write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_absolute_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        # $0000 LSR $ABCD
        self._write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_absolute_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $ABCD
        self._write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x04
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Direct Page

    def test_lsr_dp_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $0010
        self._write(mpu.memory, 0x0000, (0x46, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_dp_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        # $0000 LSR $0010
        self._write(mpu.memory, 0x0000, (0x46, 0x10))
        mpu.memory[0x0010] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_dp_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $0010
        self._write(mpu.memory, 0x0000, (0x46, 0x10))
        mpu.memory[0x0010] = 0x04
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Absolute, X-Indexed

    def test_lsr_abs_x_indexed_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_abs_x_indexed_sets_c_and_z_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_abs_x_indexed_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x04
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Direct Page, X-Indexed

    def test_lsr_dp_x_indexed_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $0010,X
        self._write(mpu.memory, 0x0000, (0x56, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_dp_x_indexed_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $0010,X
        self._write(mpu.memory, 0x0000, (0x56, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_dp_x_indexed_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $0010,X
        self._write(mpu.memory, 0x0000, (0x56, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x04
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # NOP

    def test_nop_does_nothing(self):
        mpu = self._make_mpu()
        # $0000 NOP
        mpu.memory[0x0000] = 0xEA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)

    # ORA Absolute

    def test_ora_absolute_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA $ABCD
        self._write(mpu.memory, 0x0000, (0x0D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_absolute_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        # $0000 ORA $ABCD
        self._write(mpu.memory, 0x0000, (0x0D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x82
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page

    def test_ora_dp_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA $0010
        self._write(mpu.memory, 0x0000, (0x05, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_dp_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        # $0000 ORA $0010
        self._write(mpu.memory, 0x0000, (0x05, 0x10))
        mpu.memory[0x0010] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Immediate

    def test_ora_immediate_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA #$00
        self._write(mpu.memory, 0x0000, (0x09, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_immediate_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        # $0000 ORA #$82
        self._write(mpu.memory, 0x0000, (0x09, 0x82))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Absolute, X

    def test_ora_abs_x_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ORA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_abs_x_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.x = 0x03
        # $0000 ORA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x82
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Absolute, Y

    def test_ora_abs_y_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ORA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x19, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_abs_y_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.y = 0x03
        # $0000 ORA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x19, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x82
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page Indirect, Indexed (X)

    def test_ora_ind_indexed_x_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ORA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x01, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_ind_indexed_x_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.x = 0x03
        # $0000 ORA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x01, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page Indexed, Indirect (Y)

    def test_ora_indexed_ind_y_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ORA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x11, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_indexed_ind_y_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.y = 0x03
        # $0000 ORA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x11, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page, X

    def test_ora_dp_x_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ORA $0010,X
        self._write(mpu.memory, 0x0000, (0x15, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_dp_x_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.x = 0x03
        # $0000 ORA $0010,X
        self._write(mpu.memory, 0x0000, (0x15, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ROL Accumulator

    def test_rol_accumulator_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_accumulator_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x80
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_accumulator_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_accumulator_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x40
        mpu.p |= mpu.CARRY
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x81, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_accumulator_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0x7F
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFE, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_accumulator_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFE, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Absolute

    def test_rol_absolute_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_absolute_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_absolute_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_absolute_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x40
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_absolute_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Direct Page

    def test_rol_dp_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_dp_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_dp_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Absolute, X-Indexed

    def test_rol_abs_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.x = 0x03
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_abs_x_indexed_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x03
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_abs_x_indexed_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_abs_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x40
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_abs_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_abs_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Direct Page, X-Indexed

    def test_rol_dp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_x_indexed_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        mpu.memory[0x0010 + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_x_indexed_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_dp_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_dp_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Accumulator

    def test_ror_accumulator_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR A
        mpu.memory[0x0000] = 0x6A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_accumulator_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROR A
        mpu.memory[0x0000] = 0x6A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_accumulator_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.p |= mpu.CARRY
        # $0000 ROR A
        mpu.memory[0x0000] = 0x6A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x81, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_accumulator_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR A
        mpu.memory[0x0000] = 0x6A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x81, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Absolute

    def test_ror_absolute_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_absolute_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x02
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_absolute_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x03
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Direct Page

    def test_ror_dp_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_dp_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_dp_zero_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        mpu.memory[0x0010] = 0x02
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_dp_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        mpu.memory[0x0010] = 0x03
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Absolute, X-Indexed

    def test_ror_abs_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_abs_x_indexed_z_and_c_1_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_abs_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x02
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_abs_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x03
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Direct Page, X-Indexed

    def test_ror_dp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_dp_x_indexed_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_dp_x_indexed_zero_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x02
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_dp_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x03
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # SEC

    def test_sec_sets_carry_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 SEC
        mpu.memory[0x0000] = 0x038
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # SED

    def test_sed_sets_decimal_mode_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        # $0000 SED
        mpu.memory[0x0000] = 0xF8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(mpu.DECIMAL, mpu.p & mpu.DECIMAL)

    # SEI

    def test_sei_sets_interrupt_disable_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.INTERRUPT)
        # $0000 SEI
        mpu.memory[0x0000] = 0x78
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(mpu.INTERRUPT, mpu.p & mpu.INTERRUPT)

    # STA Absolute

    def test_sta_absolute_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        # $0000 STA $ABCD
        self._write(mpu.memory, 0x0000, (0x8D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_absolute_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA $ABCD
        self._write(mpu.memory, 0x0000, (0x8D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page

    def test_sta_dp_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        # $0000 STA $0010
        self._write(mpu.memory, 0x0000, (0x85, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_dp_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA $0010
        self._write(mpu.memory, 0x0000, (0x85, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Absolute, X-Indexed

    def test_sta_abs_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 STA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x9D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_abs_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 STA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x9D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Absolute, Y-Indexed

    def test_sta_abs_y_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 STA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x99, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_abs_y_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 STA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x99, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page Indirect, Indexed (X)

    def test_sta_ind_indexed_x_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 STA ($0010,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x81, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xFEED])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_ind_indexed_x_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 STA ($0010,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x81, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page Indexed, Indirect (Y)

    def test_sta_indexed_ind_y_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 STA ($0010),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x91, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xFEED + mpu.y])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_indexed_ind_y_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 STA ($0010),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x91, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xFEED + mpu.y])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page, X-Indexed

    def test_sta_dp_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 STA $0010,X
        self._write(mpu.memory, 0x0000, (0x95, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_dp_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 STA $0010,X
        self._write(mpu.memory, 0x0000, (0x95, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STX Absolute

    def test_stx_absolute_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.x = 0xFF
        # $0000 STX $ABCD
        self._write(mpu.memory, 0x0000, (0x8E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.x)
        self.assertEqual(flags, mpu.p)

    def test_stx_absolute_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.x = 0x00
        # $0000 STX $ABCD
        self._write(mpu.memory, 0x0000, (0x8E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(flags, mpu.p)

    # STX Direct Page

    def test_stx_dp_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.x = 0xFF
        # $0000 STX $0010
        self._write(mpu.memory, 0x0000, (0x86, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.x)
        self.assertEqual(flags, mpu.p)

    def test_stx_dp_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.x = 0x00
        # $0000 STX $0010
        self._write(mpu.memory, 0x0000, (0x86, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(flags, mpu.p)

    # STX Direct Page, Y-Indexed

    def test_stx_dp_y_indexed_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.x = 0xFF
        mpu.y = 0x03
        # $0000 STX $0010,Y
        self._write(mpu.memory, 0x0000, (0x96, 0x10))
        mpu.memory[0x0010 + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.y])
        self.assertEqual(0xFF, mpu.x)
        self.assertEqual(flags, mpu.p)

    def test_stx_dp_y_indexed_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.x = 0x00
        mpu.y = 0x03
        # $0000 STX $0010,Y
        self._write(mpu.memory, 0x0000, (0x96, 0x10))
        mpu.memory[0x0010 + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.y])
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(flags, mpu.p)

    # STY Absolute

    def test_sty_absolute_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.y = 0xFF
        # $0000 STY $ABCD
        self._write(mpu.memory, 0x0000, (0x8C, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.y)
        self.assertEqual(flags, mpu.p)

    def test_sty_absolute_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.y = 0x00
        # $0000 STY $ABCD
        self._write(mpu.memory, 0x0000, (0x8C, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(flags, mpu.p)

    # STY Direct Page

    def test_sty_dp_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.y = 0xFF
        # $0000 STY $0010
        self._write(mpu.memory, 0x0000, (0x84, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.y)
        self.assertEqual(flags, mpu.p)

    def test_sty_dp_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.y = 0x00
        # $0000 STY $0010
        self._write(mpu.memory, 0x0000, (0x84, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(flags, mpu.p)

    # STY Direct Page, X-Indexed

    def test_sty_dp_x_indexed_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.y = 0xFF
        mpu.x = 0x03
        # $0000 STY $0010,X
        self._write(mpu.memory, 0x0000, (0x94, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.y)
        self.assertEqual(flags, mpu.p)

    def test_sty_dp_x_indexed_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.y = 0x00
        mpu.x = 0x03
        # $0000 STY $0010,X
        self._write(mpu.memory, 0x0000, (0x94, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(flags, mpu.p)

    # TAX

    def test_tax_transfers_accumulator_into_x(self):
        mpu = self._make_mpu()
        mpu.a = 0xAB
        mpu.x = 0x00
        # $0000 TAX
        mpu.memory[0x0000] = 0xAA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.x)

    def test_tax_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x80
        mpu.x = 0x00
        # $0000 TAX
        mpu.memory[0x0000] = 0xAA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tax_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0xFF
        # $0000 TAX
        mpu.memory[0x0000] = 0xAA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TAY

    def test_tay_transfers_accumulator_into_y(self):
        mpu = self._make_mpu()
        mpu.a = 0xAB
        mpu.y = 0x00
        # $0000 TAY
        mpu.memory[0x0000] = 0xA8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.y)

    def test_tay_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x80
        mpu.y = 0x00
        # $0000 TAY
        mpu.memory[0x0000] = 0xA8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tay_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0xFF
        # $0000 TAY
        mpu.memory[0x0000] = 0xA8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TSX

    def test_tsx_transfers_stack_pointer_into_x(self):
        mpu = self._make_mpu()
        mpu.sp = 0xAB
        mpu.x = 0x00
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.sp)
        self.assertEqual(0xAB, mpu.x)

    def test_tsx_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.sp = 0x80
        mpu.x = 0x00
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.sp)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tsx_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.sp = 0x00
        mpu.y = 0xFF
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.sp)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TXA

    def test_txa_transfers_x_into_a(self):
        mpu = self._make_mpu()
        mpu.x = 0xAB
        mpu.a = 0x00
        # $0000 TXA
        mpu.memory[0x0000] = 0x8A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.x)

    def test_txa_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x80
        mpu.a = 0x00
        # $0000 TXA
        mpu.memory[0x0000] = 0x8A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_txa_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x00
        mpu.a = 0xFF
        # $0000 TXA
        mpu.memory[0x0000] = 0x8A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TXS

    def test_txs_transfers_x_into_stack_pointer(self):
        mpu = self._make_mpu()
        mpu.x = 0xAB
        # $0000 TXS
        mpu.memory[0x0000] = 0x9A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.sp)
        self.assertEqual(0xAB, mpu.x)

    def test_txs_does_not_set_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x80
        # $0000 TXS
        mpu.memory[0x0000] = 0x9A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.sp)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_txs_does_not_set_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x00
        # $0000 TXS
        mpu.memory[0x0000] = 0x9A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.sp)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # TYA

    def test_tya_transfers_y_into_a(self):
        mpu = self._make_mpu()
        mpu.y = 0xAB
        mpu.a = 0x00
        # $0000 TYA
        mpu.memory[0x0000] = 0x98
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.y)

    def test_tya_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.y = 0x80
        mpu.a = 0x00
        # $0000 TYA
        mpu.memory[0x0000] = 0x98
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tya_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.y = 0x00
        mpu.a = 0xFF
        # $0000 TYA
        mpu.memory[0x0000] = 0x98
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0001, mpu.pc)

    #def test_decorated_addressing_modes_are_valid(self):
    #    valid_modes = [x[0] for x in assembler.Assembler.Addressing]
    #    mpu = self._make_mpu()
    #    for name, mode in mpu.disassemble:
    #        self.assertTrue(mode in valid_modes)


    # 65C02 based tests
    # Reset

    def test_reset_clears_decimal_flag(self):
        # W65C02S Datasheet, Apr 14 2009, Table 7-1 Operational Enhancements
        # NMOS 6502 decimal flag = indetermine after reset, CMOS 65C02 = 0
        mpu = self._make_mpu()
        mpu.p = mpu.DECIMAL
        mpu.reset()
        self.assertEqual(0, mpu.p & mpu.DECIMAL)


    # EOR Direct Page, Indirect

    def test_eor_dp_ind_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 EOR ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x52, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_dp_ind_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 EOR ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x52, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # INC Accumulator

    def test_inc_acc_increments_accum(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x1A
        mpu.a = 0x42
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x43, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_acc_increments_accum_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x1A
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_acc_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x1A
        mpu.a = 0x7F
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # JMP Indirect Absolute X-Indexed

    def test_jmp_iax_jumps_to_address(self):
        mpu = self._make_mpu()
        mpu.x = 2
        # $0000 JMP ($ABCD,X)
        # $ABCF Vector to $1234
        self._write(mpu.memory, 0x0000, (0x7C, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCF, (0x34, 0x12))
        mpu.step()
        self.assertEqual(0x1234, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    # LDA Direct Page, Indirect

    def test_lda_dp_ind_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_dp_ind_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # ORA Direct Page, Indirect

    def test_ora_dp_ind_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x12  # These should not affect the ORA
        mpu.x = 0x34
        # $0000 ORA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x12, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_dp_ind_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        # $0000 ORA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x12, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # STA Direct Page, Indirect

    def test_sta_dp_ind_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        # $0000 STA ($0010)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x92, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFF, mpu.memory[0xFEED])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_dp_ind_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA ($0010)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x92, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STZ Direct Page

    def test_stz_dp_stores_zero(self):
        mpu = self._make_mpu()
        mpu.memory[0x0032] = 0x88
        # #0000 STZ $32
        mpu.memory[0x0000:0x0000 + 2] = [0x64, 0x32]
        self.assertEqual(0x88, mpu.memory[0x0032])
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0x0032])
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)

    # STZ Direct Page, X-Indexed

    def test_stz_dp_x_stores_zero(self):
        mpu = self._make_mpu()
        mpu.memory[0x0032] = 0x88
        # $0000 STZ $32,X
        mpu.memory[0x0000:0x0000 + 2] = [0x74, 0x32]
        self.assertEqual(0x88, mpu.memory[0x0032])
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0x0032])
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)

    # STZ Absolute

    def test_stz_abs_stores_zero(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0x88
        # $0000 STZ $FEED
        mpu.memory[0x0000:0x0000 + 3] = [0x9C, 0xED, 0xFE]
        self.assertEqual(0x88, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)

    # STZ Absolute, X-Indexed

    def test_stz_abs_x_stores_zero(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0x88
        mpu.x = 0x0D
        # $0000 STZ $FEE0,X
        mpu.memory[0x0000:0x0000 + 3] = [0x9E, 0xE0, 0xFE]
        self.assertEqual(0x88, mpu.memory[0xFEED])
        self.assertEqual(0x0D, mpu.x)
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # TSB Direct Page

    def test_tsb_dp_ones(self):
        mpu = self._make_mpu()
        mpu.memory[0x00BB] = 0xE0
        # $0000 TSB $BD
        self._write(mpu.memory, 0x0000, [0x04, 0xBB])
        mpu.a = 0x70
        self.assertEqual(0xE0, mpu.memory[0x00BB])
        mpu.step()
        self.assertEqual(0xF0, mpu.memory[0x00BB])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    def test_tsb_dp_zeros(self):
        mpu = self._make_mpu()
        mpu.memory[0x00BB] = 0x80
        # $0000 TSB $BD
        self._write(mpu.memory, 0x0000, [0x04, 0xBB])
        mpu.a = 0x60
        self.assertEqual(0x80, mpu.memory[0x00BB])
        mpu.step()
        self.assertEqual(0xE0, mpu.memory[0x00BB])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # TSB Absolute

    def test_tsb_abs_ones(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0xE0
        # $0000 TSB $FEED
        self._write(mpu.memory, 0x0000, [0x0C, 0xED, 0xFE])
        mpu.a = 0x70
        self.assertEqual(0xE0, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0xF0, mpu.memory[0xFEED])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    def test_tsb_abs_zeros(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0x80
        # $0000 TSB $FEED
        self._write(mpu.memory, 0x0000, [0x0C, 0xED, 0xFE])
        mpu.a = 0x60
        self.assertEqual(0x80, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0xE0, mpu.memory[0xFEED])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    # TRB Direct Page

    def test_trb_dp_ones(self):
        mpu = self._make_mpu()
        mpu.memory[0x00BB] = 0xE0
        # $0000 TRB $BD
        self._write(mpu.memory, 0x0000, [0x14, 0xBB])
        mpu.a = 0x70
        self.assertEqual(0xE0, mpu.memory[0x00BB])
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0x00BB])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    def test_trb_dp_zeros(self):
        mpu = self._make_mpu()
        mpu.memory[0x00BB] = 0x80
        # $0000 TRB $BD
        self._write(mpu.memory, 0x0000, [0x14, 0xBB])
        mpu.a = 0x60
        self.assertEqual(0x80, mpu.memory[0x00BB])
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0x00BB])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # TRB Absolute

    def test_trb_abs_ones(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0xE0
        # $0000 TRB $FEED
        self._write(mpu.memory, 0x0000, [0x1C, 0xED, 0xFE])
        mpu.a = 0x70
        self.assertEqual(0xE0, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0xFEED])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    def test_trb_abs_zeros(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0x80
        # $0000 TRB $FEED
        self._write(mpu.memory, 0x0000, [0x1C, 0xED, 0xFE])
        mpu.a = 0x60
        self.assertEqual(0x80, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0xFEED])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    def test_bra_forward(self):
        mpu = self._make_mpu()
        # $0000 BRA $10
        self._write(mpu.memory, 0x0000, [0x80, 0x10])
        mpu.step()
        self.assertEqual(0x12, mpu.pc)
        self.assertEqual(2, mpu.processorCycles)

    def test_bra_backward(self):
        mpu = self._make_mpu()
        # $0240 BRA $F0
        self._write(mpu.memory, 0x0204, [0x80, 0xF0])
        mpu.pc = 0x0204
        mpu.step()
        self.assertEqual(0x1F6, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)  # Crossed boundry

    # WAI

    def test_wai_sets_waiting(self):
        mpu = self._make_mpu()
        self.assertFalse(mpu.waiting)
        # $0240 WAI
        self._write(mpu.memory, 0x0204, [0xCB])
        mpu.pc = 0x0204
        mpu.step()
        self.assertTrue(mpu.waiting)
        self.assertEqual(0x0205, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)








    # Test Helpers

    def _get_target_class(self):
        raise NotImplementedError("Target class not specified")

