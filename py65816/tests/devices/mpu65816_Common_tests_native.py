# from test_mpu6502.py, 434 tests

class Common65816NativeTests:
    """Tests common to 65816-based microprocessors Running in Native Mode"""

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

        self._write(mpu.memory, 0x0000, (0xA9, 0x01, 0x01,  # LDA #$0101
                                         0x00, 0xEA,        # BRK + skipped byte
                                         0xEA, 0xEA,        # NOP, NOP
                                         0xA9, 0x03, 0x03)) # LDA #$03

        self._write(mpu.memory, 0x0400, (0xA9, 0x02, 0x02,  # LDA #$02
                                         0x40))        # RTI

        mpu.step()  # LDA #$0101
        self.assertEqual(0x0101, mpu.a)
        self.assertEqual(0x0003, mpu.pc)
        mpu.step()  # BRK
        self.assertEqual(0x0400, mpu.pc)
        mpu.step()  # LDA #$0202
        self.assertEqual(0x0202, mpu.a)
        self.assertEqual(0x0403, mpu.pc)
        mpu.step()  # RTI

        self.assertEqual(0x0005, mpu.pc)
        mpu.step()  # A NOP
        mpu.step()  # The second NOP

        mpu.step()  # LDA #$0303
        self.assertEqual(0x0303, mpu.a)
        self.assertEqual(0x000a, mpu.pc)

    def test_brk_pushes_pbr_pc_plus_2_and_status_then_sets_pc_to_irq_vector(self):
        mpu = self._make_mpu()
        mpu.p = 0
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
        self.assertEqual(p, mpu.memory[0x1FC])  # Status
        self.assertEqual(0x1FB, mpu.sp)

        self.assertEqual(mpu.INTERRUPT, mpu.p)

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

    # BRA

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

    # BRL

    def test_brl_forward(self):
        mpu = self._make_mpu()
        # $0000 BRL $1010
        self._write(mpu.memory, 0x0000, [0x82, 0x10, 0x10])
        mpu.step()
        self.assertEqual(0x1012, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)

    def test_brl_backward(self):
        mpu = self._make_mpu()
        # $C000 BRL $8000
        self._write(mpu.memory, 0xC000, [0x82, 0x00, 0x80])
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(0x4002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)

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

    # COP

    def test_cop(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0x02, 0x0010))
        mpu.step()

    # IRQ

    def test_irq_pushes_pbr_pc_and_correct_status_then_sets_pc_to_irq_vector(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFFE6, (0x34, 0x12)) # native mode BRK
        self._write(mpu.memory, 0xFFEA, (0x88, 0x77)) # native mode NMI
        self._write(mpu.memory, 0xFFEC, (0x34, 0x12)) # native mode reserved
        self._write(mpu.memory, 0xFFEE, (0xCD, 0xAB)) # native mode IRQ
        self._write(mpu.memory, 0xFFFC, (0x34, 0x12)) # emulation mode reset
        self._write(mpu.memory, 0xFFFE, (0x34, 0x12)) # emulation mode IRQ/BRK

        mpu.p = 0 # enable interrupts
        mpu.pc = 0xC123
        mpu.pbr = 1
        mpu.irq()
        #self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x1FF])  # PBR
        self.assertEqual(0xC1, mpu.memory[0x1FE])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FD])  # PCL
        self.assertEqual(0, mpu.memory[0x1FC])  # Status
        self.assertEqual(0x1FB, mpu.sp)
        self.assertEqual(0, mpu.pbr)
        self.assertEqual(mpu.INTERRUPT, mpu.p)
        self.assertEqual(7, mpu.processorCycles)

    # JMP Absolute

    def test_jmp_abs_jumps_to_absolute_address(self):
        mpu = self._make_mpu()
        # $0000 JMP $ABCD
        self._write(mpu.memory, 0x0000, (0x4C, 0xCD, 0xAB))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

    # JMP Absolute Long

    def test_jmp_abs_long_jumps_to_absolute_address(self):
        mpu = self._make_mpu()
        # $0000 JMP $01ABCD
        self._write(mpu.memory, 0x0000, (0x5C, 0xCD, 0xAB, 0x01))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(0x01, mpu.pbr)

    # JMP Absolute Indirect

    def test_jmp_ind_does_not_have_page_wrap_bug(self):
        mpu = self._make_mpu()
        # $0000 JMP ($10FF)
        self._write(mpu.memory, 0, (0x6c, 0xFF, 0x10))
        self._write(mpu.memory, 0x10FF, (0xCD, 0xAB))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    def test_jmp_ind_jumps_to_indirect_address(self):
        mpu = self._make_mpu()
        # $0000 JMP ($ABCD)
        self._write(mpu.memory, 0x0000, (0x6C, 0x00, 0x02))
        self._write(mpu.memory, 0x0200, (0xCD, 0xAB))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

    # JMP Absolute Indirect Long

    def test_jmp_ind_long_jumps_to_indirect_address(self):
        mpu = self._make_mpu()
        # $0000 JMP ($0200)
        self._write(mpu.memory, 0x0000, (0xDC, 0x00, 0x02))
        self._write(mpu.memory, 0x0200, (0xCD, 0xAB, 0x01))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(0x01, mpu.pbr)

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

    # JSL

    def test_jsl_pushes_pb_pc_plus_3_and_sets_pc(self):
        mpu = self._make_mpu()
        # $C000 JSL $01FFD2
        self._write(mpu.memory, 0xC000, (0x22, 0xD2, 0xFF, 0x01))
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(0xFFD2, mpu.pc)
        self.assertEqual(0x01, mpu.pbr)
        self.assertEqual(0x1FC,   mpu.sp)
        self.assertEqual(0x00,   mpu.memory[0x01FF])  # PBR
        self.assertEqual(0xC0,   mpu.memory[0x01FE])  # PCH
        self.assertEqual(0x03,   mpu.memory[0x01FD])  # PCL+2

    # NMI

    def test_nmi_pushes_pc_and_correct_status_then_sets_pc_to_nmi_vector(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFFE6, (0x34, 0x12)) # native mode BRK
        self._write(mpu.memory, 0xFFEA, (0x88, 0x77)) # native mode NMI
        self._write(mpu.memory, 0xFFEC, (0x34, 0x12)) # native mode reserved
        self._write(mpu.memory, 0xFFEE, (0xCD, 0xAB)) # native mode IRQ
        self._write(mpu.memory, 0xFFFC, (0x34, 0x12)) # emulation mode reset
        self._write(mpu.memory, 0xFFFE, (0x34, 0x12)) # emulation mode IRQ/BRK

        mpu.p |= mpu.INTERRUPT # disable interrupts
        mpu.pc = 0xC123
        mpu.pbr = 1
        mpu.nmi()
        self.assertEqual(0x7788, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x1FF])  # PBR
        self.assertEqual(0xC1, mpu.memory[0x1FE])  # PCH
        self.assertEqual(0x23, mpu.memory[0x1FD])  # PCL
        self.assertEqual(mpu.INTERRUPT, mpu.memory[0x1FC])  # Status
        self.assertEqual(0x1FB, mpu.sp)
        self.assertEqual(0, mpu.pbr)
        self.assertEqual(mpu.INTERRUPT, mpu.p)
        self.assertEqual(7, mpu.processorCycles)

    # NOP

    def test_nop_does_nothing(self):
        mpu = self._make_mpu()
        # $0000 NOP
        mpu.memory[0x0000] = 0xEA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)

    # PHB

    def test_phb_pushes_b_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.a = 0xABCD
        mpu.dbr = 0x01
        # $0000 PHB
        mpu.memory[0x0000] = 0x8B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0x01, mpu.memory[0x01FF])
        self.assertEqual(0x1FE, mpu.sp)

    # PHD

    def test_phd_pushes_d_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.a = 0xABCD
        mpu.dpr = 0x0103
        # $0000 PHD
        mpu.memory[0x0000] = 0x0B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0x01, mpu.memory[0x01FF])
        self.assertEqual(0x03, mpu.memory[0x01FE])
        self.assertEqual(0x1FD, mpu.sp)

    # PHK

    def test_phk_pushes_k_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.a = 0xABCD
        mpu.pbr = 0x01
        # $0000 PHK
        mpu.memory[0x0000] = 0x4B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0x01, mpu.memory[0x01FF])
        self.assertEqual(0x1FE, mpu.sp)

    # PLB

    def test_plb_pulls_top_byte_from_stack_into_b_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLB
        mpu.memory[0x0000] = 0xAB
        mpu.memory[0x01FF] = 0x01
        mpu.sp = 0x1FE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x01,   mpu.dbr)
        self.assertEqual(0x1FF,   mpu.sp)

    # PLD

    def test_pld_pulls_top_byte_from_stack_into_d_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLD
        mpu.memory[0x0000] = 0x2B
        mpu.memory[0x01FF] = 0x01
        mpu.memory[0x01FE] = 0x01
        mpu.sp = 0x1FD
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0101,   mpu.dpr)
        self.assertEqual(0x1FF,   mpu.sp)

    # REP

    def test_rep_can_reset_all_bits(self):
        mpu = self._make_mpu()
        mpu.p = 0xFF
        # $0000 REP #$FF
        self._write(mpu.memory, 0x0000, (0xC2, 0xFF))
        mpu.step()
        self.assertEqual(0, mpu.p)

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

    # RTL

    def test_rtl_restores_pbr_and_pc_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 RTL
        mpu.memory[0x0000] = 0x6B
        self._write(mpu.memory, 0x01FD, (0x03, 0xC0, 0x01))  # PCL, PCH, PBR
        mpu.sp = 0x1FC

        mpu.step()
        self.assertEqual(0xC004, mpu.pc)
        self.assertEqual(0x01, mpu.pbr)
        self.assertEqual(0x1FF,   mpu.sp)

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

    # SEP

    def test_sep_can_set_all_bits(self):
        mpu = self._make_mpu()
        mpu.p = 0
        # $0000 SEP #$FF
        self._write(mpu.memory, 0x0000, (0xE2, 0xFF))
        mpu.step()
        self.assertEqual(0xff, mpu.p)

    # STP

    def test_stp_sets_waiting(self):
        mpu = self._make_mpu()
        self.assertFalse(mpu.waiting)
        # $0240 STP
        self._write(mpu.memory, 0x0204, [0xDB])
        mpu.pc = 0x0204
        mpu.step()
        self.assertTrue(mpu.waiting)
        self.assertEqual(0x0205, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)

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

    # WDM

    def test_wdm_does_nothing(self):
        mpu = self._make_mpu()
        # $0000 WDM
        mpu.memory[0x0000] = 0x42
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    def test_make_mpu(self):
        # test that we haven't changed key make_mpu assumptions
        # _make_mpu should:
        #   * set native mode
        #   * set 16 bit registers
        #   * clear carry
        #   * set sp to 0x1ff
        #   * set memory to 0x30000 * [0xAA]
        mpu = self._make_mpu()
        self.assertEqual(0, mpu.mode)
        self.assertEqual(0, mpu.p & mpu.MS)
        self.assertEqual(0, mpu.p & mpu.IRS)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0x1ff, mpu.sp)
        for addr in range(0x30000):
            self.assertEqual(0xAA, mpu.memory[addr])




    #def test_decorated_addressing_modes_are_valid(self):
    #    valid_modes = [x[0] for x in assembler.Assembler.Addressing]
    #    mpu = self._make_mpu()
    #    for name, mode in mpu.disassemble:
    #        self.assertTrue(mode in valid_modes)

    # Test Helpers

    def _get_target_class(self):
        raise NotImplementedError("Target class not specified")

