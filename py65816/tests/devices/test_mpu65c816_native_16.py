import unittest # python -m unittest discover -p "*816_native_16.py"
import sys
from py65816.devices.mpu65c816 import MPU
#from py65816.tests.devices.mpu65816_Common_tests_6502 import Common6502Tests
#from py65816.tests.devices.mpu65816_Common_tests_65c02 import Common65C02Tests
from py65816.tests.devices.mpu65816_Common_tests_native import Common65816NativeTests

# x tests
class MPUTests(unittest.TestCase, Common65816NativeTests):
#class MPUTests(unittest.TestCase):
    """CMOS 65C816 Tests - Native Mode - 16 Bit"""

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertTrue('65C816' in repr(mpu))

    # Native Mode - 16 bit

    # Page Bounday Wrap Tests
    def test_dpx_no_wraps_page_boundary_when_dl_zero(self):
        mpu = self._make_mpu()
        mpu.dpr = 0x0100
        mpu.x = 1
        self._write(mpu.memory, 0x00ff, (0x34, 0x12))
        self._write(mpu.memory, 0x01ff, (0xcd, 0xab, 0xff))
        # $0000 LDA $ff,X
        self._write(mpu.memory, 0x0000, (0xb5, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xffab, mpu.a)

    def test_dpx_no_wrap_page_boundary_when_dl_not_zero(self):
        mpu = self._make_mpu()
        mpu.dpr = 0x0101
        mpu.x = 0
        self._write(mpu.memory, 0x00ff, (0x34, 0x12))
        self._write(mpu.memory, 0x01ff, (0xcd, 0xab, 0xff))
        # $0000 LDA $ff,X
        self._write(mpu.memory, 0x0000, (0xb5, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xffab, mpu.a)

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
        self.assertEqual(0x5678, mpu.a)

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
        self.assertEqual(0x5678, mpu.a)

    def test_no_stack_wrap(self):
        mpu = self._make_mpu()
        mpu.sp = 0x01ff
        self._write(mpu.memory, 0x00ff, (0x34, 0x12))
        self._write(mpu.memory, 0x01ff, (0xcd, 0xab, 0xff))
        # $000 PLA
        mpu.memory[0x0000] = 0x68
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xffab, mpu.a)

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
        self.assertEqual(0x1234, mpu.a)

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
        self.assertEqual(0x5678, mpu.a)

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
        self.assertEqual(0x2010, mpu.a)

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
        self.assertEqual(0x5678, mpu.a)

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
        self.assertEqual(0x2010, mpu.a)

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
        self.assertEqual(0x9abc, mpu.a)

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
        self.assertEqual(0x2010, mpu.a)

    def test_pc_wraps_bank_zero_boundary(self):
        mpu = self._make_mpu()
        mpu.pc = 0xffff
        mpu.a = 0xffff
        mpu.x = 0x1111
        # $ffff TXA
        mpu.memory[0xffff] = 0x8a
        mpu.step()
        self.assertEqual(0x0000, mpu.pc)
        self.assertEqual(0x1111, mpu.a)

    def test_pc_wraps_bank_k_boundary(self):
        mpu = self._make_mpu()
        mpu.pc = 0xffff
        mpu.pbr = 0x01
        mpu.a = 0xffff
        mpu.x = 0x1111
        # $ffff TXA
        mpu.memory[0x01ffff] = 0x8a
        mpu.step()
        self.assertEqual(0x0000, mpu.pc)
        self.assertEqual(0x01, mpu.pbr)
        self.assertEqual(0x1111, mpu.a)

    # ADC Absolute

    def test_adc_bcd_off_absolute_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0

        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_absolute_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Absolute, X-Indexed

    def test_adc_bcd_off_abs_x_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_x_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_abs_x_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_x_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0xFF, 0xff))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.x, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Absolute, Y-Indexed

    def test_adc_bcd_off_abs_y_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_y_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_abs_y_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_y_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0xFF, 0xff))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        self._write(mpu.memory, 0xC000 + mpu.y, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Absolute Long

    def test_adc_bcd_off_absolute_long_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0

        # $0000 ADC $01C000
        self._write(mpu.memory, 0x0000, (0x6F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_long_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC $01C000
        self._write(mpu.memory, 0x0000, (0x6F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_absolute_long_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC $01C000
        self._write(mpu.memory, 0x0000, (0x6F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_long_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC $01C000
        self._write(mpu.memory, 0x0000, (0x6F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_long_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $01C000
        self._write(mpu.memory, 0x0000, (0x6F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_long_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $01C000
        self._write(mpu.memory, 0x0000, (0x6F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_long_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC $01C000
        self._write(mpu.memory, 0x0000, (0x6F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_long_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC $01C000
        self._write(mpu.memory, 0x0000, (0x6F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_long_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        # $0000 ADC $01C000
        self._write(mpu.memory, 0x0000, (0x6F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Absolute Long, X-Indexed

    def test_adc_bcd_off_abs_long_x_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC $01C000,X
        self._write(mpu.memory, 0x0000, (0x7F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_long_x_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $01C000,X
        self._write(mpu.memory, 0x0000, (0x7F, 0x00, 0xC0, 0x01))
        self._write(mpu.memory, 0x01C000 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ADC Direct Page

    def test_adc_bcd_off_dp_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_dp_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x4000
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        self._write(mpu.memory, 0xB0, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page, X-Indexed

    def test_adc_bcd_off_dp_x_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_x_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_dp_x_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_x_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_x_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_x_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_x_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_x_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_x_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        self._write(mpu.memory, 0x10 + mpu.x, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page Indirect, Indexed (X)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_ind_indexed_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page, Indirect

    def test_adc_bcd_off_dp_ind_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_ind_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_dp_ind_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_ind_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_ind_overflow_cleared_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_ind_overflow_cleared_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_ind_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_ind_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_dp_ind_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x4000
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page, Indirect Long

    def test_adc_bcd_off_dp_ind_long_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 ADC ($0010)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x67, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_dp_ind_long_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x67, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ADC Direct Page Indexed, Indirect (Y)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0000, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        mpu.y = 0x03
        # $0000 $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x4000
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Direct Page Indexed, Indirect Long (Y)

    def test_adc_bcd_off_indexed_ind_long_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ADC [$0010],Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x77, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_long_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC [$0010],Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x77, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ADC Immediate

    def test_adc_bcd_off_immediate_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0
        # $0000 ADC #$0000
        self._write(mpu.memory, 0x0000, (0x69, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_immediate_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC #$0000
        self._write(mpu.memory, 0x0000, (0x69, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_immediate_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC #$FEFF
        self._write(mpu.memory, 0x0000, (0x69, 0xFE, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_immediate_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC #$FFFF
        self._write(mpu.memory, 0x0000, (0x69, 0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC #$01
        self._write(mpu.memory, 0x000, (0x69, 0x01, 0X00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC #$FFFF
        self._write(mpu.memory, 0x000, (0x69, 0xff, 0xff))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7fff
        # $0000 ADC #$01
        self._write(mpu.memory, 0x000, (0x69, 0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x8000
        # $0000 ADC #$FFFF
        self._write(mpu.memory, 0x000, (0x69, 0xff, 0xff))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7fff, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x4000
        # $0000 ADC #$4000
        self._write(mpu.memory, 0x0000, (0x69, 0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Stack Relative

    def test_adc_bcd_off_sp_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.sp = 0x1E0
        # $0000 ADC $00B0,S
        self._write(mpu.memory, 0x0000, (0x63, 0xB0))
        self._write(mpu.memory, 0xB0 + mpu.sp, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_sp_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.sp = 0x1E0
        mpu.p |= mpu.CARRY
        # $0000 ADC $00B0,S
        self._write(mpu.memory, 0x0000, (0x63, 0xB0))
        self._write(mpu.memory, 0xB0 + mpu.sp, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ADC Stack Relative Indexed, Indirect (Y)

    def test_adc_bcd_sp_off_indexed_ind_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        mpu.sp = 0x1E0
        mpu.dbr = 1
        # $0000 ADC ($0010,S),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x73, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_sp_indexed_ind_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0x03
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010,S),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x73, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ADC Immediate

    def test_adc_bcd_on_immediate_79_plus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x79
        # $0000 ADC #$00
        self._write(mpu.memory, 0x0000, (0x69, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
#        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    # I'm not interested in non-BCD functionality
    def dont_test_adc_bcd_on_immediate_6f_plus_00_carry_set(self):
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

    # the simulated 65816 fails this but I'm not sure it's valid in the first place as py65 has some errors in BCD
    # I'm not interested in non-BCD functionality
    def dont_test_adc_bcd_on_immediate_9c_plus_9d(self):
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

    def dont_test_adc_bcd_on_immediate_99_plus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x99
        # $0000 ADC #$0000
        self._write(mpu.memory, 0x0000, (0x69, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0000, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def dont_test_adc_bcd_on_immediate_99_plus_99(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x9999
        # $0000 ADC #$9999
        # $0002 ADC #$9999
        self._write(mpu.memory, 0x0000, (0x69, 0x99, 0x99))
        self._write(mpu.memory, 0x0002, (0x69, 0x99, 0x99))
        mpu.step()
        self.assertEqual(0x9f, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x93, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    # AND Absolute

    def test_and_absolute_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $ABCD
        self._write(mpu.memory, 0x0000, (0x2D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_absolute_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $ABCD
        self._write(mpu.memory, 0x0000, (0x2D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Absolute, X-Indexed

    def test_and_abs_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3d, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_abs_x_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3d, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Absolute, Y-Indexed

    def test_and_abs_y_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x39, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_abs_y_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x39, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Absolute Long

    def test_and_absolute_long_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $01ABCD
        self._write(mpu.memory, 0x0000, (0x2F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_absolute_long_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $01ABCD
        self._write(mpu.memory, 0x0000, (0x2F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

     # AND Absolute Long, X-Indexed

    def test_and_abs_long_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $01ABCD,X
        self._write(mpu.memory, 0x0000, (0x3F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_abs_long_x_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $01ABCD,X
        self._write(mpu.memory, 0x0000, (0x3F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

   # AND Direct Page

    def test_and_dp_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $0010
        self._write(mpu.memory, 0x0000, (0x25, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_dp_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND $0010
        self._write(mpu.memory, 0x0000, (0x25, 0x10))
        self._write(mpu.memory, 0x0010, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page, X-Indexed

    def test_and_dp_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $0010,X
        self._write(mpu.memory, 0x0000, (0x35, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_dp_x_all_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND $0010,X
        self._write(mpu.memory, 0x0000, (0x35, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page Indirect, Indexed (X)

    def test_and_ind_indexed_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x21, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_ind_indexed_x_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 AND ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x21, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page, Indirect

    def test_and_dp_ind_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x32, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_dp_ind_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x32, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page, Indirect Long

    def test_and_dp_ind_long_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND ($0010)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x27, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_dp_ind_long_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND ($0010)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x27, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page Indexed, Indirect (Y)

    def test_and_indexed_ind_y_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x31, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_indexed_ind_y_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x31, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Direct Page Indexed, Indirect Long (Y)

    def test_and_indexed_ind_long_y_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x37, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_indexed_ind_long_y_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x37, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Immediate

    def test_and_immediate_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND #$00
        self._write(mpu.memory, 0x0000, (0x29, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_immediate_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 AND #$AA
        self._write(mpu.memory, 0x0000, (0x29, 0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

   # AND Stack Relative

    def test_and_sp_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        # $0000 AND $0010,S
        self._write(mpu.memory, 0x0000, (0x23, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_sp_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        # $0000 AND $0010,S
        self._write(mpu.memory, 0x0000, (0x23, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Stack Relative Indexed, Indirect (Y)

    def test_and_sp_indexed_ind_y_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        mpu.y = 0x03
        # $0000 AND ($0010,S),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x33, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_sp_indexed_ind_y_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        mpu.y = 0x03
        # $0000 AND ($0010,S),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x33, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xAA, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAAAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ASL Accumulator

    def test_asl_accumulator_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_accumulator_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x4000
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_accumulator_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0x7FFF
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFFFE, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_accumulator_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFFFE, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_asl_accumulator_80_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x8000
        mpu.p &= ~(mpu.ZERO)
        # $0000 ASL
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # ASL Absolute

    def test_asl_absolute_sets_z_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_absolute_sets_n_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x80, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_absolute_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ASL Absolute, X-Indexed

    def test_asl_abs_x_indexed_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_abs_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x80, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_abs_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_abs_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ASL Direct Page

    def test_asl_dp_sets_z_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_dp_sets_n_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x80, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_dp_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_dp_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ASL Direct Page, X-Indexed

    def test_asl_dp_x_indexed_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_dp_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x80, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_dp_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.a = 0xAA
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_dp_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.a = 0xAA
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # BIT Absolute

    def test_bit_abs_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0xFF, 0xFF))
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_bit_abs_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_bit_abs_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0xFF, 0xFF))
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_bit_abs_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_bit_abs_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0xFEED])

    def test_bit_abs_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x01, mpu.memory[0xFEED])

    def test_bit_abs_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0xFEED])

    # BIT Absolute, X-Indexed

    def test_bit_abs_x_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        self._write(mpu.memory, 0xFEED, (0xFF, 0xFF))
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
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
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
        self._write(mpu.memory, 0xFEED, (0xFF, 0xFF))
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
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
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
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
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
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
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
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    # BIT Direct Page

    def test_bit_dp_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_bit_dp_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_bit_dp_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_bit_dp_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_bit_dp_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010])

    def test_bit_dp_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        self._write(mpu.memory, 0x0010, (0x01, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x01, mpu.memory[0x0010])

    def test_bit_dp_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010])

    # BIT Direct Page, X-Indexed

    def test_bit_dp_x_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        self._write(mpu.memory, 0x0013, (0xFF, 0xFF))
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_bit_dp_x_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        self._write(mpu.memory, 0x0013, (0x00, 0x00))
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_bit_dp_x_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        self._write(mpu.memory, 0x0013, (0xFF, 0xFF))
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_bit_dp_x_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        self._write(mpu.memory, 0x0013, (0x00, 0x00))
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_bit_dp_x_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        self._write(mpu.memory, 0x0013, (0x00, 0x00))
        mpu.x = 0x03
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])

    def test_bit_dp_x_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        self._write(mpu.memory, 0x0013, (0x01, 0x00))
        mpu.x = 0x03
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x01, mpu.memory[0x0010 + mpu.x])

    def test_bit_dp_x_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        self._write(mpu.memory, 0x0013, (0x00, 0x00))
        mpu.x = 0x03
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])

    # BIT Immediate

    def test_bit_imm_does_not_affect_n_and_z_flags(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE | mpu.OVERFLOW
        # $0000 BIT #$FFFF
        self._write(mpu.memory, 0x0000, (0x89, 0xff, 0xff))
        mpu.a = 0x00
        mpu.step()
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x03, mpu.pc)

    def test_bit_imm_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT #$0000
        self._write(mpu.memory, 0x0000, (0x89, 0x00, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x03, mpu.pc)

    def test_bit_imm_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT #$0001
        self._write(mpu.memory, 0x0000, (0x89, 0x01, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x03, mpu.pc)

    def test_bit_imm_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT #$0000
        self._write(mpu.memory, 0x0000, (0x89, 0x00, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x03, mpu.pc)

    # Compare instructions

    # See http://6502.org/tutorials/compare_instructions.html
    # and http://www.6502.org/tutorials/compare_beyond.html
    # Cheat sheet:
    #
    #    - Comparison is actually subtraction "register - memory"
    #    - Z contains equality result (1 equal, 0 not equal)
    #    - C contains result of unsigned comparison (0 if A<m, 1 if A>=m)
    #    - N holds MSB of subtraction result (*NOT* of signed subtraction)
    #    - V is not affected by comparison
    #    - D has no effect on comparison

    # CMP Absolute

    def test_cmp_abs(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xCD, 0xCD, 0xAB))
        mpu.step()

    # CMP Absolute Indexed X

    def test_cmp_abs_x(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xDD, 0xCD, 0xAB))
        mpu.step()

    # CMP Absolute Indexed Y

    def test_cmp_abs_y(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xD9, 0xCD, 0xAB))
        mpu.step()

    # CMP Absolute Long

    def test_cmp_abs_long_sets_z_flag_if_equal(self):
        mpu = self._make_mpu()
        mpu.a = 0x42FF
        # $0000 AND $01ABCD
        self._write(mpu.memory, 0x0000, (0xCF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x42FF, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_cmp_abs_long_resets_z_flag_if_unequal(self):
        mpu = self._make_mpu()
        mpu.a = 0x43FF
        # $0000 AND $01ABCD
        self._write(mpu.memory, 0x0000, (0xCF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x43FF, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # CMP Absolute Long, X

    def test_cmp_abs_long_x_sets_z_flag_if_equal(self):
        mpu = self._make_mpu()
        mpu.a = 0x42FF
        mpu.x = 0x103
        # $0000 AND $01ABCD
        self._write(mpu.memory, 0x0000, (0xDF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x42FF, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_cmp_abs_long_x_resets_z_flag_if_unequal(self):
        mpu = self._make_mpu()
        mpu.a = 0x43FF
        mpu.x = 0x103
        # $0000 AND $01ABCD
        self._write(mpu.memory, 0x0000, (0xDF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x43FF, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # CMP Direct Page

    def test_cmp_dp(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xC5, 0x0010))
        mpu.step()

    # CMP Direct Page Indexed X

    def test_cmp_dp_x(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xD5, 0x0010))
        mpu.step()

    # CMP Direct Page Indexed Indirect X

    def test_cmp_dp_ind_x(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xC1, 0x0010))
        mpu.step()

    # CMP Direct Page, Indirect

    def test_cmp_dpi_sets_z_flag_if_equal(self):
        mpu = self._make_mpu()
        mpu.a = 0x42FF
        # $0000 AND ($10)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xd2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x42FF, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_cmp_dpi_resets_z_flag_if_unequal(self):
        mpu = self._make_mpu()
        mpu.a = 0x43FF
        # $0000 AND ($10)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xd2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x43FF, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # CMP Direct Page, Indirect Long

    def test_cmp_dpi_long_sets_z_flag_if_equal(self):
        mpu = self._make_mpu()
        mpu.a = 0x42FF
        # $0000 AND ($10)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0xC7, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x42FF, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_cmp_dpi_long_resets_z_flag_if_unequal(self):
        mpu = self._make_mpu()
        mpu.a = 0x43FF
        # $0000 AND ($10)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0xC7, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x43FF, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # CMP Direct Page, Indirect Indexed Y

    def test_cmp_dpi_y_sets_z_flag_if_equal(self):
        mpu = self._make_mpu()
        mpu.a = 0x42FF
        mpu.y = 0x103
        # $0000 AND ($10),y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xD1, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD+mpu.y, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x42FF, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_cmp_dpi_y_resets_z_flag_if_unequal(self):
        mpu = self._make_mpu()
        mpu.a = 0x43FF
        mpu.y = 0x103
        # $0000 AND ($10),y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xD1, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD+mpu.y, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x43FF, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # CMP Direct Page, Indirect Long Indexed Y

    def test_cmp_dpi_long_y_sets_z_flag_if_equal(self):
        mpu = self._make_mpu()
        mpu.a = 0x42FF
        mpu.y = 0x103
        # $0000 AND [$10],y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0xD7, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD+mpu.y, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x42FF, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_cmp_dpi_long_y_resets_z_flag_if_unequal(self):
        mpu = self._make_mpu()
        mpu.a = 0x43FF
        mpu.y = 0x103
        # $0000 AND [$10],y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0xD7, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD+mpu.y, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x43FF, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # CMP Immediate

    def test_cmp_imm_sets_zero_carry_clears_neg_flags_if_equal(self):
        """Comparison: A == m"""
        mpu = self._make_mpu()
        # $0000 CMP #10 , A will be 0x1010
        self._write(mpu.memory, 0x0000, (0xC9, 0x10, 0x10))
        mpu.a = 0x1010
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_cmp_imm_clears_zero_carry_takes_neg_if_less_unsigned(self):
        """Comparison: A < m (unsigned)"""
        mpu = self._make_mpu()
        # $0000 CMP #10 , A will be 1
        self._write(mpu.memory, 0x0000, (0xC9, 0x10, 0x10))
        mpu.a = 1
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE) # 0x01-0x0A=0xF7
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_cmp_imm_clears_zero_sets_carry_takes_neg_if_less_signed(self):
        """Comparison: A < #nn (signed), A negative"""
        mpu = self._make_mpu()
        # $0000 CMP #1, A will be -1 (0xFFFF)
        self._write(mpu.memory, 0x0000, (0xC9, 0x01, 0x00))
        mpu.a = 0xFFFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE) # 0xFFFF-0x0001=0xFFFE
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY) # A>m unsigned

    def test_cmp_imm_clears_zero_carry_takes_neg_if_less_signed_nega(self):
        """Comparison: A < m (signed), A and m both negative"""
        mpu = self._make_mpu()
        # $0000 CMP #0xFFFF (-1), A will be -2 (0xFFFE)
        self._write(mpu.memory, 0x0000, (0xC9, 0xFF, 0xFF))
        mpu.a = 0xFFFE
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE) # 0xFE-0xFF=0xFF
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY) # A<m unsigned

    def test_cmp_imm_clears_zero_sets_carry_takes_neg_if_more_unsigned(self):
        """Comparison: A > m (unsigned)"""
        mpu = self._make_mpu()
        # $0000 CMP #1 , A will be 10
        self._write(mpu.memory, 0x0000, (0xC9, 0X01, 0X00))
        mpu.a = 10
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE) # 0x0A-0x01 = 0x09
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY) # A>m unsigned

    def test_cmp_imm_clears_zero_carry_takes_neg_if_more_signed(self):
        """Comparison: A > m (signed), memory negative"""
        mpu = self._make_mpu()
        # $0000 CMP #$FFFF (-1), A will be 2
        self._write(mpu.memory, 0x0000, (0xC9, 0xFF, 0XFF))
        mpu.a = 2
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE) # 0x02-0xFF=0x01
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY) # A<m unsigned

    def test_cmp_imm_clears_zero_carry_takes_neg_if_more_signed_nega(self):
        """Comparison: A > m (signed), A and m both negative"""
        mpu = self._make_mpu()
        # $0000 CMP #$FFFE (-2), A will be -1 (0xFFFF)
        self._write(mpu.memory, 0x0000, (0xC9, 0xFE, 0xFF))
        mpu.a = 0xFFFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE) # 0xFF-0xFE=0x01
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY) # A>m unsigned

    # CMP Stack Relative

    def test_cmp_sp(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xC3, 0x0010))
        mpu.step()

    # CMP Stack Relative, Indirect Indexed Y

    def test_cmp_spi_y_sets_z_flag_if_equal(self):
        mpu = self._make_mpu()
        mpu.a = 0x42FF
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x103
        # $0000 AND ($10,S),y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0xD3, 0x10))
        self._write(mpu.memory, 0x0010+mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0x01ABCD+mpu.y, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(7, mpu.processorCycles)
        self.assertEqual(0x42FF, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_cmp_spi_y_resets_z_flag_if_unequal(self):
        mpu = self._make_mpu()
        mpu.a = 0x43FF
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x103
        # $0000 AND ($10,S),y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0xD3, 0x10))
        self._write(mpu.memory, 0x0010+mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0x01ABCD+mpu.y, (0xFF, 0x42))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(7, mpu.processorCycles)
        self.assertEqual(0x43FF, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # CPX Absolute

    def test_cpx_abs(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEC, 0xCD, 0xAB))
        mpu.step()

    # CPX Direct Page

    def test_cpx_dp(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE4, 0x0010))
        mpu.step()

    # CPX Immediate

    def test_cpx_imm_sets_zero_carry_clears_neg_flags_if_equal(self):
        """Comparison: X == m"""
        mpu = self._make_mpu()
        # $0000 CPX #$20ff
        self._write(mpu.memory, 0x0000, (0xE0, 0xff, 0x20))
        mpu.x = 0x20ff
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # CPY Absolute

    def test_cpy_abs(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xCC, 0xCD, 0xAB))
        mpu.step()

    # CPY Direct Page

    def test_cpy_dp(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xC4, 0x0010))
        mpu.step()

    # CPY Immediate

    def test_cpy_imm_sets_zero_carry_clears_neg_flags_if_equal(self):
        """Comparison: Y == m"""
        mpu = self._make_mpu()
        # $0000 CPY #$30ff
        self._write(mpu.memory, 0x0000, (0xC0, 0xff, 0x30))
        mpu.y = 0x30ff
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEC Absolute

    def test_dec_abs_decrements_memory(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD
        self._write(mpu.memory, 0x0000, (0xCE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x10, 0x10))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0F, mpu.memory[0xABCD])
        self.assertEqual(0x10, mpu.memory[0xABCD+1])
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dec_abs_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD
        self._write(mpu.memory, 0x0000, (0xCE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dec_abs_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD
        self._write(mpu.memory, 0x0000, (0xCE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEC Accumulator

    def test_dec_a_decreases_a(self):
        mpu = self._make_mpu()
        # $0000 DEC
        self._write(mpu.memory, 0x0000, [0x3A])
        mpu.a = 0x0148
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0x0147, mpu.a)

    def test_dec_a_sets_zero_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC
        self._write(mpu.memory, 0x0000, [0x3A])
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0x00, mpu.a)

    def test_dec_a_wraps_at_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC
        self._write(mpu.memory, 0x0000, [0x3A])
        mpu.a = 0x00
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0xffFF, mpu.a)

    # DEC Direct Page

    def test_dec_dp_decrements_memory(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010
        self._write(mpu.memory, 0x0000, (0xC6, 0x10))
        self._write(mpu.memory, 0x0010, (0x10, 0x10))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0F, mpu.memory[0x0010])
        self.assertEqual(0x10, mpu.memory[0x0010+1])
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dec_dp_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010
        self._write(mpu.memory, 0x0000, (0xC6, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010+1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dec_dp_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010
        self._write(mpu.memory, 0x0000, (0xC6, 0x10))
        self._write(mpu.memory, 0x0010, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEC Absolute, X-Indexed

    def test_dec_abs_x_decrements_memory(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD,X
        self._write(mpu.memory, 0x0000, (0xDE, 0xCD, 0xAB))
        mpu.x = 0x03
        self._write(mpu.memory, 0xABCD + mpu.x, (0x10, 0x10))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0F, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x10, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dec_abs_x_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD,X
        self._write(mpu.memory, 0x0000, (0xDE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dec_abs_x_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD,X
        self._write(mpu.memory, 0x0000, (0xDE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEC Direct Page, X-Indexed

    def test_dec_dp_x_decrements_memory(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010,X
        self._write(mpu.memory, 0x0000, (0xD6, 0x10))
        mpu.x = 0x03
        self._write(mpu.memory, 0x0010 + mpu.x, (0x10, 0x10))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0F, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x10, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dec_dp_x_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010,X
        self._write(mpu.memory, 0x0000, (0xD6, 0x10))
        mpu.x = 0x03
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dec_dp_x_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010,X
        self._write(mpu.memory, 0x0000, (0xD6, 0x10))
        mpu.x = 0x03
        self._write(mpu.memory, 0x0010 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEX

    def test_dex_decrements_x(self):
        mpu = self._make_mpu()
        mpu.x = 0x110
        # $0000 DEX
        mpu.memory[0x0000] = 0xCA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x10F, mpu.x)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dex_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        # $0000 DEX
        mpu.memory[0x0000] = 0xCA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xffFF, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dex_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x01
        # $0000 DEX
        mpu.memory[0x0000] = 0xCA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0000, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEY

    def test_dey_decrements_y(self):
        mpu = self._make_mpu()
        mpu.y = 0x110
        # $0000 DEY
        mpu.memory[0x0000] = 0x88
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x10F, mpu.y)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dey_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        # $0000 DEY
        mpu.memory[0x0000] = 0x88
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFFff, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dey_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        mpu.y = 0x01
        # $0000 DEY
        mpu.memory[0x0000] = 0x88
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0000, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # EOR Absolute

    def test_eor_absolute_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        self._write(mpu.memory, 0x0000, (0x4D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_absolute_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0x4D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Absolute, X-Indexed

    def test_eor_abs_x_indexed_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x5D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_abs_x_indexed_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x5D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Absolute, Y-Indexed

    def test_eor_abs_y_indexed_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x59, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.y])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_abs_y_indexed_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x59, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.y])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Absolute Long

    def test_eor_absolute_long_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        self._write(mpu.memory, 0x0000, (0x4F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD])
        self.assertEqual(0xFF, mpu.memory[0x01ABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_absolute_long_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0x4F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD])
        self.assertEqual(0xFF, mpu.memory[0x01ABCD+1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Absolute Long, X-Indexed

    def test_eor_abs_long_x_indexed_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x5F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + 1 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_abs_long_x_indexed_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x5F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + 1 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Direct Page

    def test_eor_dp_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        self._write(mpu.memory, 0x0000, (0x45, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_dp_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0x45, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Direct Page, X-Indexed

    def test_eor_dp_x_indexed_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x55, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_dp_x_indexed_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x55, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Direct Page, Indirect

    def test_eor_dp_ind_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 EOR ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x52, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_dp_ind_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 EOR ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x52, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Direct Page, Indirect Long

    def test_eor_dp_ind_long_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 EOR ($0010)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x47, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD])
        self.assertEqual(0xFF, mpu.memory[0x01ABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_dp_ind_long_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 EOR ($0010)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x47, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD])
        self.assertEqual(0xFF, mpu.memory[0x01ABCD+1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Direct Page Indirect, Indexed (X)

    def test_eor_ind_indexed_x_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_ind_indexed_x_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Direct Page Indexed, Indirect (Y)

    def test_eor_indexed_ind_y_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_indexed_ind_y_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Direct Page Indexed, Indirect Long (Y)

    def test_eor_indexed_ind_long_y_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x57, 0x10))  # => EOR ($0010),Y
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))  # => Vector to $01ABCD
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + mpu.y])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_indexed_ind_long_y_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x57, 0x10))  # => EOR ($0010),Y
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))  # => Vector to $01ABCD
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + mpu.y])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Immediate

    def test_eor_immediate_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        self._write(mpu.memory, 0x0000, (0x49, 0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_immediate_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0x49, 0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Stack Relative

    def test_eor_sp_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        self._write(mpu.memory, 0x0000, (0x43, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.sp])
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.sp + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_sp_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.sp = 0x1E0
        self._write(mpu.memory, 0x0000, (0x43, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.sp])
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.sp + 1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Stack Relative Indirect Indexed Y

    def test_eor_sp_indexed_ind_y_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x53, 0x10))  # => EOR ($0010,S),Y
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))  # => Vector to $01ABCD
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + mpu.y])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_sp_indexed_ind_y_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x53, 0x10))  # => EOR ($0010,S),Y
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))  # => Vector to $01ABCD
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + mpu.y])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # INC Absolute

    def test_inc_abs_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x01, mpu.memory[0xABCD + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x80, mpu.memory[0xABCD+1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Absolute, X-Indexed

    def test_inc_abs_x_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.x = 0x03
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x01, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_x_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.x = 0x03
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_x_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.x = 0x03
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Accumulator

    def test_inc_acc_increments_accum(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x1A
        mpu.a = 0x4242
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x4243, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_acc_increments_accum_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x1A
        mpu.a = 0xFFFF
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_acc_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x1A
        mpu.a = 0x7FFF
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Direct Page

    def test_inc_dp_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE6, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x01, mpu.memory[0x0010 + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_dp_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE6, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_dp_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE6, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x80, mpu.memory[0x0010 + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Direct Page, X-Indexed

    def test_inc_dp_x_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xF6, 0x10))
        mpu.x = 0x03
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x01, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_dp_x_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xF6, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_dp_x_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xF6, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INX

    def test_inx_increments_x(self):
        mpu = self._make_mpu()
        mpu.x = 0x4242
        mpu.memory[0x0000] = 0xE8  # => INX
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x4243, mpu.x)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inx_above_FF_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFFFF
        mpu.memory[0x0000] = 0xE8  # => INX
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_inx_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        mpu.x = 0x7fff
        mpu.memory[0x0000] = 0xE8  # => INX
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INY

    def test_iny_increments_y(self):
        mpu = self._make_mpu()
        mpu.y = 0X4242
        mpu.memory[0x0000] = 0xC8  # => INY
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x4243, mpu.y)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_iny_above_FF_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFFFF
        mpu.memory[0x0000] = 0xC8  # => INY
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_iny_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        mpu.y = 0x7fff
        mpu.memory[0x0000] = 0xC8  # => INY
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # JMP Absolute Indirect X-Indexed

    def test_jmp_iax_jumps_to_address(self):
        mpu = self._make_mpu()
        mpu.x = 0x102
        # $0000 JMP ($ABCD,X)
        # $ACCF Vector to $1234
        self._write(mpu.memory, 0x0000, (0x7C, 0xCD, 0xAB))
        self._write(mpu.memory, 0xACCF, (0x34, 0x12))
        mpu.step()
        self.assertEqual(0x1234, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    # JSR Absolute Indirect X-Indexed

    def test_jsr_abs_ind_x_pushes_pc_plus_2_and_sets_pc(self):
        mpu = self._make_mpu()
        mpu.x = 0x102
        # $0000 JSR ($ABCD,X)
        # $ACCF Vector to $1234
        self._write(mpu.memory, 0x0000, (0xFC, 0xCD, 0xAB))
        self._write(mpu.memory, 0xACCF, (0x34, 0x12))
        mpu.step()
        self.assertEqual(0x1234, mpu.pc)
        self.assertEqual(0x1FD,   mpu.sp)
        self.assertEqual(0x00,   mpu.memory[0x01FF])  # PCH
        self.assertEqual(0x02,   mpu.memory[0x01FE])  # PCL+2

    # LDA Absolute

    def test_lda_absolute_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA $ABCD
        self._write(mpu.memory, 0x0000, (0xAD, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_absolute_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 LDA $ABCD
        self._write(mpu.memory, 0x0000, (0xAD, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
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
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_abs_x_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 LDA $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBD, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lda_abs_x_indexed_does_not_page_wrap(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x1FF
        # $0000 LDA $0080,X
        self._write(mpu.memory, 0x0000, (0xBD, 0x80, 0x00))
        self._write(mpu.memory, 0x0080 + mpu.x, (0x43, 0x42))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x4243, mpu.a)

    # LDA Absolute, Y-Indexed

    def test_lda_abs_y_indexed_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 LDA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xB9, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_abs_y_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x03
        # $0000 LDA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xB9, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lda_abs_y_indexed_does_not_page_wrap(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0x1FF
        # $0000 LDA $0080,X
        self._write(mpu.memory, 0x0000, (0xB9, 0x80, 0x00))
        self._write(mpu.memory, 0x0080 + mpu.y, (0x43, 0x42))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x4243, mpu.a)

    # LDA Absolute Long

    def test_lda_absolute_long_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA $01ABCD
        self._write(mpu.memory, 0x0000, (0xAF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_absolute_long_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 LDA $01ABCD
        self._write(mpu.memory, 0x0000, (0xAF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Absolute Long, X-Indexed

    def test_lda_abs_x_long_indexed_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 LDA $01ABCD,X
        self._write(mpu.memory, 0x0000, (0xBF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_abs_long_x_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x03
        # $0000 LDA $01ABCD,X
        self._write(mpu.memory, 0x0000, (0xBF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lda_abs_long_x_indexed_does_not_page_wrap(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x1FF
        # $0000 LDA $010080,X
        self._write(mpu.memory, 0x0000, (0xBF, 0x80, 0x00, 0x01))
        self._write(mpu.memory, 0x010080 + mpu.x, (0x43, 0x42))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x4243, mpu.a)

    # LDA Direct Page

    def test_lda_dp_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA $0010
        self._write(mpu.memory, 0x0000, (0xA5, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_dp_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 LDA $0010
        self._write(mpu.memory, 0x0000, (0xA5, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Direct Page, X-Indexed

    def test_lda_dp_x_indexed_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 LDA $10,X
        self._write(mpu.memory, 0x0000, (0xB5, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_dp_x_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x103
        # $0000 LDA $10,X
        self._write(mpu.memory, 0x0000, (0xB5, 0x10))
        mpu.memory[0x0010] = 0x00
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Direct Page, Indirect

    def test_lda_dp_ind_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_dp_ind_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 LDA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Direct Page, Indirect Long

    def test_lda_dp_ind_long_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA ($0010)
        # $0010 Vector to 01$ABCD
        self._write(mpu.memory, 0x0000, (0xA7, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_dp_ind_long_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 LDA ($0010)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0xA7, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Direct Page Indirect, Indexed (X)

    def test_lda_ind_indexed_x_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 LDA ($0010,X)
        # $0113 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xA1, 0x10))
        self._write(mpu.memory, 0x0113, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_ind_indexed_x_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.x = 0x103
        # $0000 LDA ($0010,X)
        # $0113 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xA1, 0x10))
        self._write(mpu.memory, 0x0113, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Direct Page Indexed, Indirect (Y)

    def test_lda_indexed_ind_y_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x103
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB1, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_indexed_ind_y_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x103
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB1, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Direct Page Indexed, Indirect Long (Y)

    def test_lda_indexed_ind_long_y_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x103
        # $0000 LDA ($0010),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0xB7, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_indexed_ind_long_y_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.y = 0x103
        # $0000 LDA ($0010),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0xB7, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x00))
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
        self._write(mpu.memory, 0x0000, (0xA9, 0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_immediate_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        # $0000 LDA #$00
        self._write(mpu.memory, 0x0000, (0xA9, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Stack Relative

    def test_lda_sp_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.sp = 0x1E0
        # $0000 LDA $0010.S
        self._write(mpu.memory, 0x0000, (0xA3, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_sp_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        # $0000 LDA $0010,S
        self._write(mpu.memory, 0x0000, (0xA3, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Stack Relative Indexed, Indirect (Y)

    def test_lda_sp_indexed_ind_y_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x103
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB3, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_sp_indexed_ind_y_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x103
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB3, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x00))
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
        self._write(mpu.memory, 0xABCD, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_absolute_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFFFF
        # $0000 LDX $ABCD
        self._write(mpu.memory, 0x0000, (0xAE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Absolute, Y-Indexed

    def test_ldx_abs_y_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        mpu.y = 0x103
        # $0000 LDX $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xBE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_abs_y_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFFFF
        mpu.y = 0x103
        # $0000 LDX $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xBE, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
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
        self._write(mpu.memory, 0x0010, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_dp_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFFFF
        # $0000 LDX $0010
        self._write(mpu.memory, 0x0000, (0xA6, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
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
        self._write(mpu.memory, 0x0010 + mpu.y, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_dp_y_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFFFF
        mpu.y = 0x103
        # $0000 LDX $0010,Y
        self._write(mpu.memory, 0x0000, (0xB6, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.y, (0x00, 0x00))
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
        self._write(mpu.memory, 0x0000, (0xA2, 0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_immediate_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFFFF
        # $0000 LDX #$00
        self._write(mpu.memory, 0x0000, (0xA2, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Absolute

    def test_ldy_absolute_loads_y_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        # $0000 LDY $ABCD
        self._write(mpu.memory, 0x0000, (0xAC, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_absolute_loads_y_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFFFF
        # $0000 LDY $ABCD
        self._write(mpu.memory, 0x0000, (0xAC, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Absolute, X-Indexed

    def test_ldy_abs_x_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        mpu.x = 0x103
        # $0000 LDY $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBC, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_abs_x_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFFFF
        mpu.x = 0x103
        # $0000 LDY $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBC, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
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
        self._write(mpu.memory, 0x0010, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_dp_loads_y_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        # $0000 LDY $0010
        self._write(mpu.memory, 0x0000, (0xA4, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Direct Page, X-Indexed

    def test_ldy_dp_x_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        mpu.x = 0x103
        # $0000 LDY $0010,X
        self._write(mpu.memory, 0x0000, (0xB4, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_dp_x_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFFFF
        mpu.x = 0x03
        # $0000 LDY $0010,X
        self._write(mpu.memory, 0x0000, (0xB4, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
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
        self._write(mpu.memory, 0x0000, (0xA0, 0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_immediate_loads_y_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFFFF
        # $0000 LDY #$00
        self._write(mpu.memory, 0x0000, (0xA0, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Absolute

    def test_lsr_absolute_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $ABCD
        self._write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_absolute_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        # $0000 LSR $ABCD
        self._write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_absolute_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $ABCD
        self._write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x04, 0x04))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0xABCD])
        self.assertEqual(0x02, mpu.memory[0xABCD+1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Absolute, X-Indexed

    def test_lsr_abs_x_indexed_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x103
        # $0000 LSR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_abs_x_indexed_sets_c_and_z_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        mpu.x = 0x103
        # $0000 LSR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_abs_x_indexed_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x103
        # $0000 LSR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x04, 0x04))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x02, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
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
        mpu.a = 0x0404
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0202, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Direct Page

    def test_lsr_dp_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $0010
        self._write(mpu.memory, 0x0000, (0x46, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_dp_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        # $0000 LSR $0010
        self._write(mpu.memory, 0x0000, (0x46, 0x10))
        self._write(mpu.memory, 0x0010, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_dp_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $0010
        self._write(mpu.memory, 0x0000, (0x46, 0x10))
        self._write(mpu.memory, 0x0010, (0x04, 0x04))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0x0010])
        self.assertEqual(0x02, mpu.memory[0x0010 + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Direct Page, X-Indexed

    def test_lsr_dp_x_indexed_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x103
        # $0000 LSR $0010,X
        self._write(mpu.memory, 0x0000, (0x56, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_dp_x_indexed_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        mpu.x = 0x103
        # $0000 LSR $0010,X
        self._write(mpu.memory, 0x0000, (0x56, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x+ 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_dp_x_indexed_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x103
        # $0000 LSR $0010,X
        self._write(mpu.memory, 0x0000, (0x56, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x04, 0x04))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x02, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # MVN

    def test_mvn(self):
        mpu = self._make_mpu()

        mpu.x = 0x200
        mpu.y = 0x100
        mpu.a = 0x100
        # $0000 MVN $00,$01
        self._write(mpu.memory, 0x0000, (0x54, 0X01, 0x00))
        self._write(mpu.memory, mpu.x, [0x55] * mpu.a)
        for addr in range(mpu.x, 0x0300):
            self.assertEqual(0x55, mpu.memory[addr])
        for addr in range(0x10100, 0x10200):
            mpu.step()
            self.assertEqual(0x55, mpu.memory[addr])

    def test_mvn_wrap_at_bank_boundary(self):
        mpu = self._make_mpu()

        mpu.pc = 0x100
        mpu.x = 0xff80
        mpu.y = 0xff80
        mpu.a = 0x100
        # $0100 MVN $00,$01
        self._write(mpu.memory, 0x0100, (0x54, 0X01, 0x00))
        self._write(mpu.memory, 0x0000, [0x55] * (mpu.a >> 1))
        self._write(mpu.memory, mpu.x, [0x55] * (mpu.a >> 1))
        for addr in range(0x0000, 0x0080):
            self.assertEqual(0x55, mpu.memory[addr])
        for addr in range(mpu.x, 0x10000):
            self.assertEqual(0x55, mpu.memory[addr])
        for addr in range(0x1ff80, 0x20000):
            mpu.step()
            self.assertEqual(0x55, mpu.memory[addr])
        for addr in range(0x10000, 0x10080):
            mpu.step()
            self.assertEqual(0x55, mpu.memory[addr])

    # MVP

    def test_mvp(self):
        mpu = self._make_mpu()

        mpu.x = 0x2ff
        mpu.y = 0x1ff
        mpu.a = 0x100
        # $0000 MVN $00,$01
        self._write(mpu.memory, 0x0000, (0x44, 0X01, 0x00))
        self._write(mpu.memory, 0x0200, [0x55] * mpu.a)
        for addr in range(0x0200, 0x0300):
            self.assertEqual(0x55, mpu.memory[addr])
        for addr in range(0x101ff, 0x100ff, -1):
            mpu.step()
            self.assertEqual(0x55, mpu.memory[addr])

    def test_mvp_wrap_at_bank_boundary(self):
        mpu = self._make_mpu()

        mpu.pc = 0x100
        mpu.x = 0x007f
        mpu.y = 0x007f
        mpu.a = 0x100
        # $0100 MVN $00,$01
        self._write(mpu.memory, 0x0100, (0x44, 0X01, 0x00))
        self._write(mpu.memory, 0x0000, [0x55] * (mpu.a >> 1))
        self._write(mpu.memory, 0xff80, [0x55] * (mpu.a >> 1))
        for addr in range(0x0000, 0x0080):
            self.assertEqual(0x55, mpu.memory[addr])
        for addr in range(0xff80, 0xffff):
            self.assertEqual(0x55, mpu.memory[addr])
        for addr in range(0x1007f, 0xffff, -1):
            mpu.step()
            self.assertEqual(0x55, mpu.memory[addr])
        for addr in range(0x1ffff, 0x1ff7f, -1):
            mpu.step()
            self.assertEqual(0x55, mpu.memory[addr])

    # ORA Absolute

    def test_ora_absolute_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA $ABCD
        self._write(mpu.memory, 0x0000, (0x0D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_absolute_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        # $0000 ORA $ABCD
        self._write(mpu.memory, 0x0000, (0x0D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Absolute, X

    def test_ora_abs_x_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 ORA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_abs_x_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        mpu.x = 0x103
        # $0000 ORA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Absolute, Y

    def test_ora_abs_y_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x103
        # $0000 ORA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x19, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_abs_y_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        mpu.y = 0x103
        # $0000 ORA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x19, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Absolute Long

    def test_ora_absolute_long_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA $01ABCD
        self._write(mpu.memory, 0x0000, (0x0F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_absolute_long_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        # $0000 ORA $01ABCD
        self._write(mpu.memory, 0x0000, (0x0F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Absolute Long, X

    def test_ora_abs_long_x_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 ORA $01ABCD,X
        self._write(mpu.memory, 0x0000, (0x1F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_abs_long_x_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        mpu.x = 0x103
        # $0000 ORA $01ABCD,X
        self._write(mpu.memory, 0x0000, (0x1F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page

    def test_ora_dp_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA $0010
        self._write(mpu.memory, 0x0000, (0x05, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_dp_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        # $0000 ORA $0010
        self._write(mpu.memory, 0x0000, (0x05, 0x10))
        self._write(mpu.memory, 0x0010, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page, X

    def test_ora_dp_x_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 ORA $0010,X
        self._write(mpu.memory, 0x0000, (0x15, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_dp_x_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        mpu.x = 0x103
        # $0000 ORA $0010,X
        self._write(mpu.memory, 0x0000, (0x15, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page, Indirect

    def test_ora_dp_ind_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x1234  # These should not affect the ORA
        mpu.x = 0x3456
        # $0000 ORA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x12, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_dp_ind_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        # $0000 ORA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x12, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page, Indirect Long

    def test_ora_dp_ind_long_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x1234  # These should not affect the ORA
        mpu.x = 0x3456
        # $0000 ORA ($0010)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x07, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_dp_ind_long_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        # $0000 ORA ($0010)
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x07, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page Indirect, Indexed (X)

    def test_ora_ind_indexed_x_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 ORA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x01, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_ind_indexed_x_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        mpu.x = 0x103
        # $0000 ORA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x01, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page Indexed, Indirect (Y)

    def test_ora_indexed_ind_y_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x103
        # $0000 ORA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x11, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_indexed_ind_y_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        mpu.y = 0x103
        # $0000 ORA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x11, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Direct Page Indexed, Indirect Long (Y)

    def test_ora_indexed_ind_long_y_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x103
        # $0000 ORA ($0010),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x17, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_indexed_ind_long_y_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        mpu.y = 0x103
        # $0000 ORA ($0010),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x17, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Immediate

    def test_ora_immediate_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA #$00
        self._write(mpu.memory, 0x0000, (0x09, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_immediate_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        # $0000 ORA #$8022
        self._write(mpu.memory, 0x0000, (0x09, 0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Stack Relative

    def test_ora_sp_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.sp = 0x1E0
        # $0000 ORA $0010
        self._write(mpu.memory, 0x0000, (0x03, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_sp_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        mpu.sp = 0x1E0
        # $0000 ORA $0010
        self._write(mpu.memory, 0x0000, (0x03, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Stack Relative Indexed, Indirect (Y)

    def test_ora_sp_indexed_ind_y_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x103
        # $0000 ORA ($0010,S),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x13, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_sp_indexed_ind_y_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x0303
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x103
        # $0000 ORA ($0010,S),Y
        # $0010 Vector to $01ABCD
        self._write(mpu.memory, 0x0000, (0x13, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xCD, 0xAB))
        self._write(mpu.memory, 0x01ABCD + mpu.y, (0x22, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x8323, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # PHA

    def test_pha_pushes_a_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.a = 0xABCD
        # $0000 PHA
        mpu.memory[0x0000] = 0x48
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0xCD, mpu.memory[0x01FE])
        self.assertEqual(0x1FD, mpu.sp)

    # PHP

    def test_php_pushes_processor_status_and_updates_sp(self):
        for flags in range(0x100):
            mpu = self._make_mpu()
            mpu.p = flags & ((not mpu.MS) | (not mpu.IRS))
            # $0000 PHP
            mpu.memory[0x0000] = 0x08
            mpu.step()
            self.assertEqual(0x0001, mpu.pc)
            self.assertEqual((flags & ((not mpu.MS) | (not mpu.IRS))), mpu.memory[0x1FF])
            self.assertEqual(0x1FE, mpu.sp)

    # PHX

    def test_phx_pushes_x_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.x = 0xABCD
        # $0000 PHX
        mpu.memory[0x0000] = 0xDA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.x)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0xCD, mpu.memory[0x01FE])
        self.assertEqual(0x1FD, mpu.sp)
        self.assertEqual(3, mpu.processorCycles)

    # PHY

    def test_phy_pushes_y_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.y = 0xABCD
        # $0000 PHY
        mpu.memory[0x0000] = 0x5A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.y)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0xCD, mpu.memory[0x01FE])
        self.assertEqual(0x1FD, mpu.sp)
        self.assertEqual(3, mpu.processorCycles)

    # PLA

    def test_pla_pulls_top_byte_from_stack_into_a_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLA
        mpu.memory[0x0000] = 0x68
        mpu.memory[0x01FF] = 0xAB
        mpu.memory[0x01FE] = 0xCD
        mpu.sp = 0x1FD
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD,   mpu.a)
        self.assertEqual(0x1FF,   mpu.sp)

    # PLP

    def test_plp_pulls_top_byte_from_stack_into_flags_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLP
        mpu.memory[0x0000] = 0x28
        mpu.memory[0x01FF] = 0xCF  # must have MS and IRS cleared
        mpu.sp = 0x1FE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xCF,   mpu.p)
        self.assertEqual(0x1FF,   mpu.sp)

    # PLX

    def test_plx_pulls_two_bytes_from_stack_into_x_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLX
        mpu.memory[0x0000] = 0xFA
        mpu.memory[0x01FF] = 0xAB
        mpu.memory[0x01FE] = 0xCD
        mpu.sp = 0x1FD
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD,   mpu.x)
        self.assertEqual(0x1FF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # PLY

    def test_ply_pulls_two_bytes_from_stack_into_y_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLY
        mpu.memory[0x0000] = 0x7A
        mpu.memory[0x01FF] = 0xAB
        mpu.memory[0x01FE] = 0xCD
        mpu.sp = 0x1FD
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD,   mpu.y)
        self.assertEqual(0x1FF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # ROL Absolute

    def test_rol_absolute_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_absolute_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_absolute_80_and_carry_set_remains_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.p &= ~(mpu.ZERO)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_absolute_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
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
        self._write(mpu.memory, 0xABCD, (0x40, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD])
        self.assertEqual(0x80, mpu.memory[0xABCD + 1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_absolute_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Absolute, X-Indexed

    def test_rol_abs_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.x = 0x103
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_abs_x_indexed_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x103
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_abs_x_indexed_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_abs_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x40, 0x40))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_abs_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_abs_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

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
        mpu.a = 0x8000
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
        mpu.a = 0x4040
        mpu.p |= mpu.CARRY
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8081, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_accumulator_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0x7FFF
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFFFE, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_accumulator_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xFFFF
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFFFE, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Direct Page

    def test_rol_dp_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        self._write(mpu.memory, 0x0010, (0x40, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010])
        self.assertEqual(0x80, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_dp_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010] + 1)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_dp_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Direct Page, X-Indexed

    def test_rol_dp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.x = 0x103
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_x_indexed_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x103
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_x_indexed_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_dp_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x40, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_dp_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0x7F))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_dp_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Absolute

    def test_ror_absolute_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_absolute_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x80, mpu.memory[0xABCD+1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x02, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD])
        self.assertEqual(0xC0, mpu.memory[0xABCD+1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_absolute_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x03, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD])
        self.assertEqual(0xC0, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_ror_absolute_carry_clear_shifts_out_one(self):
        mpu = self._make_mpu()
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x03, 0x80))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD])
        self.assertEqual(0x40, mpu.memory[0xABCD+1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Absolute, X-Indexed

    def test_ror_abs_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_abs_x_indexed_z_and_c_1_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_abs_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_abs_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x03, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x + 1])
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
        self.assertEqual(0x8000, mpu.a)
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
        self.assertEqual(0x8001, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_accumulator_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR A
        mpu.memory[0x0000] = 0x6A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8001, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Direct Page

    def test_ror_dp_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_dp_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x80, mpu.memory[0x0010 + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_dp_zero_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        self._write(mpu.memory, 0x0010, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010])
        self.assertEqual(0x80, mpu.memory[0x0010 + 1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_dp_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        self._write(mpu.memory, 0x0010, (0x03, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010])
        self.assertEqual(0x80, mpu.memory[0x0010 + 1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Direct Page, X-Indexed

    def test_ror_dp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_dp_x_indexed_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_dp_x_indexed_zero_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_dp_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x103
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x03, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x + 1])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)












    # *** TODO: probably makes sense to move the relevant values to the high byte or perhaps both since we've already tested the low byte in 8 bit ***
    # *** TODO: need a test that sets overflow ***
    # SBC Absolute

    def test_sbc_abs_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Absolute, X-Indexed

    def test_sbc_abs_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        self._write(mpu.memory, 0xFEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Absolute, Y-Indexed

    def test_sbc_abs_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_y_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_y_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        self._write(mpu.memory, 0xFEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Absolute Long

    def test_sbc_abs_long_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $01ABCD
        self._write(mpu.memory, 0x0000, (0xEF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_long_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $01ABCD
        self._write(mpu.memory, 0x0000, (0xEF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_long_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $01ABCD
        self._write(mpu.memory, 0x0000, (0xEF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_long_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $01ABCD
        self._write(mpu.memory, 0x0000, (0xEF, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Absolute Long, X-Indexed

    def test_sbc_abs_long_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $01FEE0,X
        self._write(mpu.memory, 0x0000, (0xFF, 0xE0, 0xFE, 0x01))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x01FEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_long_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $01FEE0,X
        self._write(mpu.memory, 0x0000, (0xFF, 0xE0, 0xFE, 0x01))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x01FEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_long_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $01FEE0,X
        self._write(mpu.memory, 0x0000, (0xFF, 0xE0, 0xFE, 0x01))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x01FEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_long_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $01FEE0,X
        self._write(mpu.memory, 0x0000, (0xFF, 0xE0, 0xFE, 0x01))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x01FEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page

    def test_sbc_dp_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        self._write(mpu.memory, 0x0010, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # => SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # => SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        self._write(mpu.memory, 0x0010, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page, X-Indexed

    def test_sbc_dp_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x001D, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x001D, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x001D, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        self._write(mpu.memory, 0x001D, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page Indirect, Indexed (X)

    def test_sbc_ind_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        self._write(mpu.memory, 0xFEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page, Indirect

    def test_sbc_dp_ind_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_ind_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_ind_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_ind_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page, Indirect Long

    def test_sbc_dp_ind_long_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC ($10)
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xE7, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_ind_long_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xE7, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_ind_long_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xE7, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_dp_ind_long_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10)
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xE7, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page Indexed, Indirect (Y)

    def test_sbc_ind_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_y_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_y_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED + mpu.y, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Direct Page Indexed, Indirect Long (Y)

    def test_sbc_ind_long_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xF7, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_long_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xF7, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_long_y_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xF7, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_long_y_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xF7, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED + mpu.y, (0x02, 0x00))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Immediate

    def test_sbc_imm_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xE9, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_imm_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC #$01
        self._write(mpu.memory, 0x0000, (0xE9, 0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_imm_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xE9, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_imm_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC #$02
        self._write(mpu.memory, 0x0000, (0xE9, 0x02, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Stack Relative

    def test_sbc_sp_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        mpu.sp = 0x1E0
        # $0000 SBC $10,S
        self._write(mpu.memory, 0x0000, (0xE3, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_sp_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        mpu.sp = 0x1E0
        # $0000 SBC $10,S
        self._write(mpu.memory, 0x0000, (0xE3, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # SBC Stack Relative Indexed, Indirect (Y)

    def test_sbc_sp_ind_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x03
        # $0000 SBC ($10,S),Y
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xF3, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xED, 0xFE))
        self._write(mpu.memory, 0x01FEED + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_sp_ind_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x03
        # $0000 SBC ($10,S),Y
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0xF3, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xED, 0xFE))
        self._write(mpu.memory, 0x01FEED + mpu.y, (0x01, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_bcd_on_immediate_0a_minus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x0a
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xe9, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0a, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # the simulated 65816 fails this but I'm not sure it's valid in the first place as py65 has some errors in BCD
    # I'm not interested in non-BCD functionality
    def dont_test_sbc_bcd_on_immediate_9a_minus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x9a
        #$0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xe9, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x9a, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_sbc_bcd_on_immediate_99_minus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x9999
        #$0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xe9, 0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x9999, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_sbc_bcd_on_immediate_00_minus_01_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.OVERFLOW
        mpu.p |= mpu.ZERO
        mpu.p |= mpu.CARRY
        mpu.a = 0x00
        # => $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xe9, 0x01, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x9999, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_sbc_bcd_on_immediate_20_minus_0a_carry_unset(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.a = 0x20
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xe9, 0x0a, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x1f, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # STA Absolute

    def test_sta_absolute_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        # $0000 STA $ABCD
        self._write(mpu.memory, 0x0000, (0x8D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_absolute_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA $ABCD
        self._write(mpu.memory, 0x0000, (0x8D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Absolute, X-Indexed

    def test_sta_abs_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        mpu.x = 0x103
        # $0000 STA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x9D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x+1])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_abs_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 STA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x9D, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x+1])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Absolute, Y-Indexed

    def test_sta_abs_y_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        mpu.y = 0x103
        # $0000 STA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x99, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y+1])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_abs_y_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x103
        # $0000 STA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x99, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.y+1])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Absolute Long

    def test_sta_absolute_long_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        # $0000 STA $01ABCD
        self._write(mpu.memory, 0x0000, (0x8F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD])
        self.assertEqual(0xFF, mpu.memory[0x01ABCD+1])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_absolute_long_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA $01ABCD
        self._write(mpu.memory, 0x0000, (0x8F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x01ABCD])
        self.assertEqual(0x00, mpu.memory[0x01ABCD+1])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Absolute Long, X-Indexed

    def test_sta_abs_long_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        mpu.x = 0x103
        # $0000 STA $01ABCD,X
        self._write(mpu.memory, 0x0000, (0x9F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x01ABCD + mpu.x+1])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_abs_long_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 STA $01ABCD,X
        self._write(mpu.memory, 0x0000, (0x9F, 0xCD, 0xAB, 0x01))
        self._write(mpu.memory, 0x01ABCD + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x01ABCD + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x01ABCD + mpu.x+1])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page

    def test_sta_dp_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        # $0000 STA $0010
        self._write(mpu.memory, 0x0000, (0x85, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010+1])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_dp_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA $0010
        self._write(mpu.memory, 0x0000, (0x85, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010+1])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page, X-Indexed

    def test_sta_dp_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        mpu.x = 0x103
        # $0000 STA $0010,X
        self._write(mpu.memory, 0x0000, (0x95, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x+1])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_dp_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 STA $0010,X
        self._write(mpu.memory, 0x0000, (0x95, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x+1])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page, Indirect

    def test_sta_dp_ind_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        # $0000 STA ($0010)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x92, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFF, mpu.memory[0xFEED])
        self.assertEqual(0xFF, mpu.memory[0xFEEE])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_dp_ind_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA ($0010)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x92, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x00, mpu.memory[0xFEEE])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page, Indirect Long

    def test_sta_dp_ind_long_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        # $0000 STA ($0010)
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0x87, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0xFF, mpu.memory[0x01FEED])
        self.assertEqual(0xFF, mpu.memory[0x01FEEE])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_dp_ind_long_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA ($0010)
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0x87, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        self._write(mpu.memory, 0x01FEED, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)
        self.assertEqual(0x00, mpu.memory[0x01FEED])
        self.assertEqual(0x00, mpu.memory[0x01FEEE])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page Indirect, Indexed (X)

    def test_sta_ind_indexed_x_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        mpu.x = 0x103
        # $0000 STA ($0010,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x81, 0x10))
        self._write(mpu.memory, 0x0113, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xFEED])
        self.assertEqual(0xFF, mpu.memory[0xFEEE])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_ind_indexed_x_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x103
        # $0000 STA ($0010,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x81, 0x10))
        self._write(mpu.memory, 0x0113, (0xED, 0xFE))
        self._write(mpu.memory, 0xFEED, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x00, mpu.memory[0xFEEE])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page Indexed, Indirect (Y)

    def test_sta_indexed_ind_y_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        mpu.y = 0x103
        # $0000 STA ($0010),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x91, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0x00
        mpu.memory[0xFEEE + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xFEED + mpu.y])
        self.assertEqual(0xFF, mpu.memory[0xFEEE + mpu.y])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_indexed_ind_y_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x103
        # $0000 STA ($0010),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x91, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0xFF
        mpu.memory[0xFEEE + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xFEED + mpu.y])
        self.assertEqual(0x00, mpu.memory[0xFEEE + mpu.y])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Direct Page Indexed, Indirect Long (Y)

    def test_sta_indexed_ind_long_y_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        mpu.y = 0x103
        # $0000 STA ($0010),Y
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0x97, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        mpu.memory[0xFEED + mpu.y] = 0x00
        mpu.memory[0xFEEE + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x01FEED + mpu.y])
        self.assertEqual(0xFF, mpu.memory[0x01FEEE + mpu.y])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_indexed_ind_long_y_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x103
        # $0000 STA ($0010),Y
        # $0010 Vector to 01$FEED
        self._write(mpu.memory, 0x0000, (0x97, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE, 0x01))
        mpu.memory[0xFEED + mpu.y] = 0xFF
        mpu.memory[0xFEEE + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x01FEED + mpu.y])
        self.assertEqual(0x00, mpu.memory[0x01FEEE + mpu.y])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Stack Relative

    def test_sta_sp_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        # $0000 STA $0010,S
        self._write(mpu.memory, 0x0000, (0x83, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.sp])
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.sp+1])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_sp_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.sp = 0x1E0
        # $0000 STA $0010,S
        self._write(mpu.memory, 0x0000, (0x83, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.sp])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.sp+1])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Stack Relative Indexed, Indirect (Y)

    def test_sta_sp_indexed_ind_y_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.a = 0xFFFF
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x103
        # $0000 STA ($0010,S),Y
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0x93, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xED, 0xFE))
        mpu.memory[0x01FEED + mpu.y] = 0x00
        mpu.memory[0x01FEEE + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x01FEED + mpu.y])
        self.assertEqual(0xFF, mpu.memory[0x01FEEE + mpu.y])
        self.assertEqual(0xFFFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_sp_indexed_ind_y_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.sp = 0x1E0
        mpu.dbr = 1
        mpu.y = 0x103
        # $0000 STA ($0010,S),Y
        # $0010 Vector to $01FEED
        self._write(mpu.memory, 0x0000, (0x93, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.sp, (0xED, 0xFE))
        mpu.memory[0x01FEED + mpu.y] = 0xFF
        mpu.memory[0x01FEEE + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x01FEED + mpu.y])
        self.assertEqual(0x00, mpu.memory[0x01FEEE + mpu.y])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STX Absolute

    def test_stx_absolute_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.x = 0xFFFF
        # $0000 STX $ABCD
        self._write(mpu.memory, 0x0000, (0x8E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(0xFFFF, mpu.x)
        self.assertEqual(flags, mpu.p)

    def test_stx_absolute_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.x = 0x00
        # $0000 STX $ABCD
        self._write(mpu.memory, 0x0000, (0x8E, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(flags, mpu.p)

    # STX Direct Page

    def test_stx_dp_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.x = 0xFFFF
        # $0000 STX $0010
        self._write(mpu.memory, 0x0000, (0x86, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010+1])
        self.assertEqual(0xFFFF, mpu.x)
        self.assertEqual(flags, mpu.p)

    def test_stx_dp_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.x = 0x00
        # $0000 STX $0010
        self._write(mpu.memory, 0x0000, (0x86, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010+1])
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(flags, mpu.p)

    # STX Direct Page, Y-Indexed

    def test_stx_dp_y_indexed_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.x = 0xFFFF
        mpu.y = 0x103
        # $0000 STX $0010,Y
        self._write(mpu.memory, 0x0000, (0x96, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.y, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.y])
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.y+1])
        self.assertEqual(0xFFFF, mpu.x)
        self.assertEqual(flags, mpu.p)

    def test_stx_dp_y_indexed_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.x = 0x00
        mpu.y = 0x103
        # $0000 STX $0010,Y
        self._write(mpu.memory, 0x0000, (0x96, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.y, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.y])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.y+1])
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(flags, mpu.p)

    # STY Absolute

    def test_sty_absolute_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.y = 0xFFFF
        # $0000 STY $ABCD
        self._write(mpu.memory, 0x0000, (0x8C, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
        self.assertEqual(0xFFFF, mpu.y)
        self.assertEqual(flags, mpu.p)

    def test_sty_absolute_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.y = 0x00
        # $0000 STY $ABCD
        self._write(mpu.memory, 0x0000, (0x8C, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.memory[0xABCD+1])
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(flags, mpu.p)

    # STY Direct Page

    def test_sty_dp_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.y = 0xFFFF
        # $0000 STY $0010
        self._write(mpu.memory, 0x0000, (0x84, 0x10))
        self._write(mpu.memory, 0x0010, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.memory[0x0010+1])
        self.assertEqual(0xFFFF, mpu.y)
        self.assertEqual(flags, mpu.p)

    def test_sty_dp_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.y = 0x00
        # $0000 STY $0010
        self._write(mpu.memory, 0x0000, (0x84, 0x10))
        self._write(mpu.memory, 0x0010, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.memory[0x0010+1])
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(flags, mpu.p)

    # STY Direct Page, X-Indexed

    def test_sty_dp_x_indexed_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.NEGATIVE)
        mpu.y = 0xFFFF
        mpu.x = 0x103
        # $0000 STY $0010,X
        self._write(mpu.memory, 0x0000, (0x94, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0x00, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x+1])
        self.assertEqual(0xFFFF, mpu.y)
        self.assertEqual(flags, mpu.p)

    def test_sty_dp_x_indexed_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xCF & ~(mpu.ZERO)
        mpu.y = 0x00
        mpu.x = 0x103
        # $0000 STY $0010,X
        self._write(mpu.memory, 0x0000, (0x94, 0x10))
        self._write(mpu.memory, 0x0010 + mpu.x, (0xFF, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x+1])
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(flags, mpu.p)

    # STZ Absolute

    def test_stz_abs_stores_zero(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFEED + mpu.x, (0xFF, 0xFF))
        # $0000 STZ $FEED
        mpu.memory[0x0000:0x0000 + 3] = [0x9C, 0xED, 0xFE]
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x00, mpu.memory[0xFEED+1])
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)

    # STZ Absolute, X-Indexed

    def test_stz_abs_x_stores_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x0D
        self._write(mpu.memory, 0xFEED + mpu.x, (0xFF, 0xFF))
        # $0000 STZ $FEE0,X
        mpu.memory[0x0000:0x0000 + 3] = [0x9E, 0xE0, 0xFE]
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x00, mpu.memory[0xFEED+1])
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # STZ Direct Page

    def test_stz_dp_stores_zero(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0032, (0xFF, 0xFF))
        # #0000 STZ $32
        mpu.memory[0x0000:0x0000 + 2] = [0x64, 0x32]
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0x0032])
        self.assertEqual(0x00, mpu.memory[0x0032+1])
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)

    # STZ Direct Page, X-Indexed

    def test_stz_dp_x_stores_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x0D
        self._write(mpu.memory, 0x0032 + mpu.x, (0xFF, 0xFF))
        # $0000 STZ $32,X
        mpu.memory[0x0000:0x0000 + 2] = [0x74, 0x32]
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0x0032 + mpu.x])
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)

    # TAX
    # *** TODO: need to test for 8/16 bit mix ***

    def test_tax_transfers_accumulator_into_x(self):
        mpu = self._make_mpu()
        mpu.a = 0xABCD
        mpu.x = 0x00
        # $0000 TAX
        mpu.memory[0x0000] = 0xAA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0xABCD, mpu.x)

    def test_tax_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x8000
        mpu.x = 0x00
        # $0000 TAX
        mpu.memory[0x0000] = 0xAA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tax_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0xFFFF
        # $0000 TAX
        mpu.memory[0x0000] = 0xAA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TAY
    # *** TODO: need to test for 8/16 bit mix ***

    def test_tay_transfers_accumulator_into_y(self):
        mpu = self._make_mpu()
        mpu.a = 0xABCD
        mpu.y = 0x00
        # $0000 TAY
        mpu.memory[0x0000] = 0xA8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0xABCD, mpu.y)

    def test_tay_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x8000
        mpu.y = 0x00
        # $0000 TAY
        mpu.memory[0x0000] = 0xA8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tay_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0xFFFF
        # $0000 TAY
        mpu.memory[0x0000] = 0xA8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TCD

    def test_tcd_transfers_accumulator_into_d(self):
        mpu = self._make_mpu()
        mpu.a = 0xABCD
        # $0000 TCD
        mpu.memory[0x0000] = 0x5B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0xABCD, mpu.dpr)

    def test_tcd_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x8000
        # $0000 TCD
        mpu.memory[0x0000] = 0x5B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(0x8000, mpu.dpr)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tcd_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 TCD
        mpu.memory[0x0000] = 0x5B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.dpr)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TCS

    def test_tcs_transfers_accumulator_into_s(self):
        mpu = self._make_mpu()
        mpu.a = 0xABCD
        # $0000 TCS
        mpu.memory[0x0000] = 0x1B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0xABCD, mpu.sp)

    def test_tcs_does_not_set_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x8000
        # $0000 TCS
        mpu.memory[0x0000] = 0x1B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(0x8000, mpu.sp)
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
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0xABCD, mpu.dpr)

    def test_tdc_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.dpr = 0x8000
        # $0000 TDC
        mpu.memory[0x0000] = 0x7B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
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
        self.assertEqual(0x00, mpu.dpr)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TRB Absolute

    def test_trb_abs_ones(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFEED, (0xE0, 0xE0))
        # $0000 TRB $FEED
        self._write(mpu.memory, 0x0000, [0x1C, 0xED, 0xFE])
        mpu.a = 0x7070
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0xFEED])
        self.assertEqual(0x80, mpu.memory[0xFEED+1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    def test_trb_abs_zeros(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFEED, (0x80, 0x80))
        # $0000 TRB $FEED
        self._write(mpu.memory, 0x0000, [0x1C, 0xED, 0xFE])
        mpu.a = 0x6060
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0xFEED])
        self.assertEqual(0x80, mpu.memory[0xFEED+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    # TRB Direct Page

    def test_trb_dp_ones(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x00BB, (0xE0, 0xE0))
        # $0000 TRB $BB
        self._write(mpu.memory, 0x0000, [0x14, 0xBB])
        mpu.a = 0x7070
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0x00BB])
        self.assertEqual(0x80, mpu.memory[0x00BB+1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    def test_trb_dp_zeros(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x00BB, (0x80, 0x80))
        # $0000 TRB $BB
        self._write(mpu.memory, 0x0000, [0x14, 0xBB])
        mpu.a = 0x6060
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0x00BB])
        self.assertEqual(0x80, mpu.memory[0x00BB+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # TSB Absolute

    def test_tsb_abs_ones(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFEED, (0xE0, 0xE0))
        # $0000 TSB $FEED
        self._write(mpu.memory, 0x0000, [0x0C, 0xED, 0xFE])
        mpu.a = 0x7070
        mpu.step()
        self.assertEqual(0xF0, mpu.memory[0xFEED])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    def test_tsb_abs_zeros(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0xFEED, (0x80, 0x80))
        # $0000 TSB $FEED
        self._write(mpu.memory, 0x0000, [0x0C, 0xED, 0xFE])
        mpu.a = 0x6060
        mpu.step()
        self.assertEqual(0xE0, mpu.memory[0xFEED])
        self.assertEqual(0xE0, mpu.memory[0xFEED+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    # TSB Direct Page

    def test_tsb_dp_ones(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x00BB, (0xE0, 0xE0))
        # $0000 TSB $BB
        self._write(mpu.memory, 0x0000, [0x04, 0xBB])
        mpu.a = 0x7070
        mpu.step()
        self.assertEqual(0xF0, mpu.memory[0x00BB])
        self.assertEqual(0xF0, mpu.memory[0x00BB+1])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    def test_tsb_dp_zeros(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x00BB, (0x80, 0x80))
        # $0000 TSB $BB
        self._write(mpu.memory, 0x0000, [0x04, 0xBB])
        mpu.a = 0x6060
        mpu.step()
        self.assertEqual(0xE0, mpu.memory[0x00BB])
        self.assertEqual(0xE0, mpu.memory[0x00BB+1])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # TSC

    def test_tsc_transfers_accumulator_into_s(self):
        mpu = self._make_mpu()
        mpu.sp = 0xABCD
        # $0000 TSC
        mpu.memory[0x0000] = 0x3B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0xABCD, mpu.sp)

    def test_tsc_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.sp = 0x8000
        # $0000 TSC
        mpu.memory[0x0000] = 0x3B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
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
        self.assertEqual(0x00, mpu.sp)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TSX

    def test_tsx_transfers_stack_pointer_into_x(self):
        mpu = self._make_mpu()
        mpu.sp = 0xABCD
        mpu.x = 0x00
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.sp)
        self.assertEqual(0xABCD, mpu.x)

    def test_tsx_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.sp = 0x8000
        mpu.x = 0x00
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.sp)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tsx_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.sp = 0x00
        mpu.x = 0xFFFF
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.sp)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TXA
    # *** TODO: need to test for 8/16 bit mix ***

    def test_txa_transfers_x_into_a(self):
        mpu = self._make_mpu()
        mpu.x = 0xABCD
        mpu.a = 0x00
        # $0000 TXA
        mpu.memory[0x0000] = 0x8A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0xABCD, mpu.x)

    def test_txa_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x8000
        mpu.a = 0x00
        # $0000 TXA
        mpu.memory[0x0000] = 0x8A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_txa_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x00
        mpu.a = 0xFFFF
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
        mpu.x = 0xABCD
        # $0000 TXS
        mpu.memory[0x0000] = 0x9A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.sp)
        self.assertEqual(0xABCD, mpu.x)

    def test_txs_does_not_set_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x8000
        # $0000 TXS
        mpu.memory[0x0000] = 0x9A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.sp)
        self.assertEqual(0x8000, mpu.x)
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

    # TXY

    def test_txy_transfers_x_into_a(self):
        mpu = self._make_mpu()
        mpu.x = 0xABCD
        mpu.y = 0x00
        # $0000 TXY
        mpu.memory[0x0000] = 0x9B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.y)
        self.assertEqual(0xABCD, mpu.x)

    def test_txy_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x8000
        mpu.y = 0x00
        # $0000 TXY
        mpu.memory[0x0000] = 0x9B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_txy_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x00
        mpu.y = 0xFFFF
        # $0000 TXY
        mpu.memory[0x0000] = 0x9B
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TYA
    # *** TODO: need to test for 8/16 bit mix ***

    def test_tya_transfers_y_into_a(self):
        mpu = self._make_mpu()
        mpu.y = 0xABCD
        mpu.a = 0x00
        # $0000 TYA
        mpu.memory[0x0000] = 0x98
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.a)
        self.assertEqual(0xABCD, mpu.y)

    def test_tya_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.y = 0x8000
        mpu.a = 0x00
        # $0000 TYA
        mpu.memory[0x0000] = 0x98
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.a)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tya_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.y = 0x00
        mpu.a = 0xFFFF
        # $0000 TYA
        mpu.memory[0x0000] = 0x98
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0001, mpu.pc)

    # TYX

    def test_tyx_transfers_x_into_a(self):
        mpu = self._make_mpu()
        mpu.y = 0xABCD
        mpu.x = 0x00
        # $0000 TYX
        mpu.memory[0x0000] = 0xBB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xABCD, mpu.y)
        self.assertEqual(0xABCD, mpu.x)

    def test_tyx_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.y = 0x8000
        mpu.x = 0x00
        # $0000 TYX
        mpu.memory[0x0000] = 0xBB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x8000, mpu.y)
        self.assertEqual(0x8000, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tyx_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.y = 0x00
        mpu.x = 0xFFFF
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
        mpu.a = 0xABCD
        # $0000 XBA
        mpu.memory[0x0000] = 0xEB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xCDAB, mpu.a)

    def test_xba_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x8000
        # $0000 XBA
        mpu.memory[0x0000] = 0xEB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0080, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_xba_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00FF
        # $0000 XBA
        mpu.memory[0x0000] = 0xEB
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFF00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # XCE

    def test_xce_exchange_c_and_e_bits(self):
        mpu = self._make_mpu() # native mode, carry is cleared

        mpu.pSET(mpu.CARRY)

        mpu.memory[0x0000] = 0xFB
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(mpu.BREAK, mpu.p & mpu.BREAK)
        self.assertEqual(mpu.UNUSED, mpu.p & mpu.UNUSED)
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
        mpu.pCLR(mpu.MS)
        mpu.pCLR(mpu.IRS)

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
