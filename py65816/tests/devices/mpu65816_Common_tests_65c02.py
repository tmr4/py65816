# from test_mpu65c02.py, 71 tests
class Common65C02Tests:
    """CMOS 65C02 Tests"""

    # Reset

    def test_reset_clears_decimal_flag(self):
        # W65C02S Datasheet, Apr 14 2009, Table 7-1 Operational Enhancements
        # NMOS 6502 decimal flag = indetermine after reset, CMOS 65C02 = 0
        mpu = self._make_mpu()
        mpu.p = mpu.DECIMAL
        mpu.reset()
        self.assertEqual(0, mpu.p & mpu.DECIMAL)

    # ADC Zero Page, Indirect

    def test_adc_bcd_off_zp_ind_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_ind_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_zp_ind_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFE
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_ind_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_ind_overflow_cleared_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_ind_overflow_cleared_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_ind_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_ind_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_ind_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x40
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Zero Page, Indirect

    def test_and_zp_ind_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x32, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_zp_ind_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x32, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xAA
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # BIT (Absolute, X-Indexed)

    def test_bit_abs_x_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_stores_result_of_and_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x01
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x01, mpu.memory[0xFEED])
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    # BIT (Immediate)

    def test_bit_imm_does_not_affect_n_and_z_flags(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE | mpu.OVERFLOW
        # $0000 BIT #$FF
        self._write(mpu.memory, 0x0000, (0x89, 0xff))
        mpu.a = 0x00
        mpu.step()
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x02, mpu.pc)

    def test_bit_imm_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT #$00
        self._write(mpu.memory, 0x0000, (0x89, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x02, mpu.pc)

    def test_bit_imm_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT #$01
        self._write(mpu.memory, 0x0000, (0x89, 0x01))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x02, mpu.pc)

    def test_bit_imm_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT #$00
        self._write(mpu.memory, 0x0000, (0x89, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x02, mpu.pc)

    # BIT (Zero Page, X-Indexed)

    def test_bit_zp_x_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0xFF
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_bit_zp_x_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x00
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_bit_zp_x_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0xFF
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_bit_zp_x_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x00
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_bit_zp_x_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x00
        mpu.x = 0x03
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])

    def test_bit_zp_x_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x01
        mpu.x = 0x03
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x01, mpu.memory[0x0010 + mpu.x])

    def test_bit_zp_x_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x00
        mpu.x = 0x03
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])

    # CMP Zero Page, Indirect

    def test_cmp_zpi_sets_z_flag_if_equal(self):
        mpu = self._make_mpu()
        mpu.a = 0x42
        # $0000 AND ($10)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xd2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x42
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x42, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_cmp_zpi_resets_z_flag_if_unequal(self):
        mpu = self._make_mpu()
        mpu.a = 0x43
        # $0000 AND ($10)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xd2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x42
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x43, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # EOR Zero Page, Indirect

    def test_eor_zp_ind_flips_bits_over_setting_z_flag(self):
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

    def test_eor_zp_ind_flips_bits_over_setting_n_flag(self):
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

    # LDA Zero Page, Indirect

    def test_lda_zp_ind_loads_a_sets_n_flag(self):
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

    def test_lda_zp_ind_loads_a_sets_z_flag(self):
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

    # ORA Zero Page, Indirect

    def test_ora_zp_ind_zeroes_or_zeros_sets_z_flag(self):
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

    def test_ora_zp_ind_turns_bits_on_sets_n_flag(self):
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

    # STA Zero Page, Indirect

    def test_sta_zp_ind_stores_a_leaves_a_and_n_flag_unchanged(self):
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

    def test_sta_zp_ind_stores_a_leaves_a_and_z_flag_unchanged(self):
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

    # SBC Zero Page, Indirect

    def test_sbc_zp_ind_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_ind_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_ind_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_ind_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x02
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # STZ Zero Page

    def test_stz_zp_stores_zero(self):
        mpu = self._make_mpu()
        mpu.memory[0x0032] = 0x88
        # #0000 STZ $32
        mpu.memory[0x0000:0x0000 + 2] = [0x64, 0x32]
        self.assertEqual(0x88, mpu.memory[0x0032])
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0x0032])
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)

    # STZ Zero Page, X-Indexed

    def test_stz_zp_x_stores_zero(self):
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

    # TSB Zero Page

    def test_tsb_zp_ones(self):
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

    def test_tsb_zp_zeros(self):
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

    # TRB Zero Page

    def test_trb_zp_ones(self):
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

    def test_trb_zp_zeros(self):
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

    def test_dec_a_decreases_a(self):
        mpu = self._make_mpu()
        # $0000 DEC A
        self._write(mpu.memory, 0x0000, [0x3A])
        mpu.a = 0x48
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0x47, mpu.a)

    def test_dec_a_sets_zero_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC A
        self._write(mpu.memory, 0x0000, [0x3A])
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0x00, mpu.a)

    def test_dec_a_wraps_at_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC A
        self._write(mpu.memory, 0x0000, [0x3A])
        mpu.a = 0x00
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0xFF, mpu.a)

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
        return devices.mpu65c02.MPU
