import unittest
import sys
from py65816.devices.mpu65c816 import MPU
#from py65816.tests.devices.mpu65816_Common_tests_6502 import Common6502Tests
#from py65816.tests.devices.mpu65816_Common_tests_65c02 import Common65C02Tests

# 2 tests
#class MPUTests(unittest.TestCase, Common65816NativeTests):
class MPUTests(unittest.TestCase):
    """CMOS 65C816 Tests - Native Mode - 16 Bit"""

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertTrue('65C816' in repr(mpu))

    # Native Mode - 16 bit

    # ADC Absolute

    def test_adc_bcd_off_absolute_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0

        self.assertEqual(0x30000, len(mpu.memory))

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

#    def test_eor_absolute_flips_bits_over_setting_z_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0xFFFF
#        self._write(mpu.memory, 0x0000, (0x4D, 0xCD, 0xAB))
#        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x00, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD])
#        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
#        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
#
#    def test_eor_absolute_flips_bits_over_setting_n_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0x00
#        self._write(mpu.memory, 0x0000, (0x4D, 0xCD, 0xAB))
#        self._write(mpu.memory, 0xABCD, (0xFF, 0xFF))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0xFFFF, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD])
#        self.assertEqual(0xFF, mpu.memory[0xABCD+1])
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#
#    # EOR Absolute, X-Indexed
#
#    def test_eor_abs_x_indexed_flips_bits_over_setting_z_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0xFFFF
#        mpu.x = 0x03
#        self._write(mpu.memory, 0x0000, (0x5D, 0xCD, 0xAB))
#        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0xFF))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x00, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
#        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.x])
#        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
#
#    def test_eor_abs_x_indexed_flips_bits_over_setting_n_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0x00
#        mpu.x = 0x03
#        self._write(mpu.memory, 0x0000, (0x5D, 0xCD, 0xAB))
#        self._write(mpu.memory, 0xABCD + mpu.x, (0xFF, 0xFF))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0xFFFF, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
#        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.x])
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#
#    # EOR Absolute, Y-Indexed
#
#    def test_eor_abs_y_indexed_flips_bits_over_setting_z_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0xFFFF
#        mpu.y = 0x03
#        self._write(mpu.memory, 0x0000, (0x59, 0xCD, 0xAB))
#        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x00, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
#        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.y])
#        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
#
#    def test_eor_abs_y_indexed_flips_bits_over_setting_n_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0x00
#        mpu.y = 0x03
#        self._write(mpu.memory, 0x0000, (0x59, 0xCD, 0xAB))
#        self._write(mpu.memory, 0xABCD + mpu.y, (0xFF, 0xFF))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0xFFFF, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
#        self.assertEqual(0xFF, mpu.memory[0xABCD + 1 + mpu.y])
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#
#    # EOR Direct Page
#
#    def test_eor_dp_flips_bits_over_setting_z_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0xFF
#        self._write(mpu.memory, 0x0000, (0x45, 0x10))
#        mpu.memory[0x0010] = 0xFF
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0x00, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0x0010])
#        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
#
#    def test_eor_dp_flips_bits_over_setting_n_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0x00
#        self._write(mpu.memory, 0x0000, (0x45, 0x10))
#        mpu.memory[0x0010] = 0xFF
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0xFF, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0x0010])
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#
#    # EOR Direct Page, X-Indexed
#
#    def test_eor_dp_x_indexed_flips_bits_over_setting_z_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0xFF
#        mpu.x = 0x03
#        self._write(mpu.memory, 0x0000, (0x55, 0x10))
#        mpu.memory[0x0010 + mpu.x] = 0xFF
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0x00, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
#        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
#
#    def test_eor_dp_x_indexed_flips_bits_over_setting_n_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0x00
#        mpu.x = 0x03
#        self._write(mpu.memory, 0x0000, (0x55, 0x10))
#        mpu.memory[0x0010 + mpu.x] = 0xFF
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0xFF, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#
#    # EOR Direct Page Indirect, Indexed (X)
#
#    def test_eor_ind_indexed_x_flips_bits_over_setting_z_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0xFF
#        mpu.x = 0x03
#        self._write(mpu.memory, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
#        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
#        mpu.memory[0xABCD] = 0xFF
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0x00, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD])
#        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
#
#    def test_eor_ind_indexed_x_flips_bits_over_setting_n_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0x00
#        mpu.x = 0x03
#        self._write(mpu.memory, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
#        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
#        mpu.memory[0xABCD] = 0xFF
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0xFF, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD])
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#
#    # EOR Direct Page Indexed, Indirect (Y)
#
#    def test_eor_indexed_ind_y_flips_bits_over_setting_z_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0xFF
#        mpu.y = 0x03
#        self._write(mpu.memory, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
#        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
#        mpu.memory[0xABCD + mpu.y] = 0xFF
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0x00, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
#        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
#
#    def test_eor_indexed_ind_y_flips_bits_over_setting_n_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0x00
#        mpu.y = 0x03
#        self._write(mpu.memory, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
#        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
#        mpu.memory[0xABCD + mpu.y] = 0xFF
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0xFF, mpu.a)
#        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#
#    # EOR Immediate
#
#    def test_eor_immediate_flips_bits_over_setting_z_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0xFF
#        self._write(mpu.memory, 0x0000, (0x49, 0xFF))
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0x00, mpu.a)
#        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
#
#    def test_eor_immediate_flips_bits_over_setting_n_flag(self):
#        mpu = self._make_mpu()
#        mpu.a = 0x00
#        self._write(mpu.memory, 0x0000, (0x49, 0xFF))
#        mpu.step()
#        self.assertEqual(0x0002, mpu.pc)
#        self.assertEqual(0xFF, mpu.a)
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.ZERO)










    # *** TODO: probably makes sense to move the relevant values to the high byte or perhaps both since we've already tested the low byte in 8 bit ***
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

#    def test_sbc_bcd_on_immediate_0a_minus_00_carry_set(self):
#        mpu = self._make_mpu()
#        mpu.p |= mpu.DECIMAL
#        mpu.p |= mpu.CARRY
#        mpu.a = 0x0a
#        # $0000 SBC #$00
#        self._write(mpu.memory, 0x0000, (0xe9, 0x00, 0x00))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x0a, mpu.a)
#        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
#
#    def test_sbc_bcd_on_immediate_9a_minus_00_carry_set(self):
#        mpu = self._make_mpu()
#        mpu.p |= mpu.DECIMAL
#        mpu.p |= mpu.CARRY
#        mpu.a = 0x9a
#        #$0000 SBC #$00
#        self._write(mpu.memory, 0x0000, (0xe9, 0x00, 0x00))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x9a, mpu.a)
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
#
#    def test_sbc_bcd_on_immediate_00_minus_01_carry_set(self):
#        mpu = self._make_mpu()
#        mpu.p |= mpu.DECIMAL
#        mpu.p |= mpu.OVERFLOW
#        mpu.p |= mpu.ZERO
#        mpu.p |= mpu.CARRY
#        mpu.a = 0x00
#        # => $0000 SBC #$00
#        self._write(mpu.memory, 0x0000, (0xe9, 0x01, 0x00))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x99, mpu.a)
#        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#        self.assertEqual(0, mpu.p & mpu.CARRY)
#
#    def test_sbc_bcd_on_immediate_20_minus_0a_carry_unset(self):
#        mpu = self._make_mpu()
#        mpu.p |= mpu.DECIMAL
#        mpu.a = 0x20
#        # $0000 SBC #$00
#        self._write(mpu.memory, 0x0000, (0xe9, 0x0a, 0x00))
#        mpu.step()
#        self.assertEqual(0x0003, mpu.pc)
#        self.assertEqual(0x1f, mpu.a)
#        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
#        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
#        self.assertEqual(0, mpu.p & mpu.ZERO)
#        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)








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
