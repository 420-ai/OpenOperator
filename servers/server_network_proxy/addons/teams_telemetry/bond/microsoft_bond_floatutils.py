"""
microsoft_bond_floatutils.py
Copyright: Microsoft 2016

This class will be used to convert float/double to byte array in environments without struct support.

Format: IEEE-754, littleEndian, http://en.wikipedia.org/wiki/IEEE_754-1985

Note:
1. Don't have negative zero. All zero will be positive zero.
2. If the buffer array passed to ConvertArrayToFloat() is an invalid NaN or Infinity value,
   an exception will be raised.
"""
from ..bond.microsoft_bond_exception import Exception as BondException

class FloatUtils:
    _float_zero = [0x00, 0x00, 0x00, 0x00]
    _double_zero = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    _float_infinity = [0x00, 0x00, 0x80, 0x7F]
    _float_neg_infinity = [0x00, 0x00, 0x80, 0xFF]
    _double_infinity = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x7F]
    _double_neg_infinity = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0xFF]

    @staticmethod
    def convert_number_to_array(num, is_double):
        """Convert a Python float to an array of bytes"""
        if not num:
            return FloatUtils._double_zero if is_double else FloatUtils._float_zero

        exponent_bits = 11 if is_double else 8
        precision_bits = 52 if is_double else 23

        # follow IEEE-754, exponent bias is 2^(k-1)-1 where k is the number of bits
        # in the exponent: http://en.wikipedia.org/wiki/Exponent_bias
        bias = (1 << (exponent_bits - 1)) - 1
        min_exponent = 1 - bias
        max_exponent = bias

        sign = 1 if num < 0 else 0
        num = abs(num)
        int_part = int(num)
        float_part = num - int_part

        length = 2 * (bias + 2) + precision_bits
        buffer = [0] * length
        i = 0

        # calculate the int_part
        i = bias + 2
        while i > 0 and int_part:
            i -= 1
            buffer[i] = int_part % 2
            int_part = int(int_part / 2)

        # calculate the float_part
        i = bias + 1
        while i < length - 1 and float_part > 0:
            float_part *= 2
            if float_part >= 1:
                i += 1
                buffer[i] = 1
                float_part -= 1
            else:
                i += 1
                buffer[i] = 0

        # find the first 1
        first_bit = 0
        while first_bit < length and not buffer[first_bit]:
            first_bit += 1

        # calculate exponent
        exponent = bias + 1 - first_bit

        # calculate round
        last_bit = first_bit + precision_bits
        if last_bit + 1 < length and buffer[last_bit + 1]:
            for i in range(last_bit, first_bit, -1):
                buffer[i] = 1 - buffer[i]
                if buffer[i]:
                    break
            if i == first_bit:
                exponent += 1

        # check overflow
        if exponent > max_exponent or int_part:
            if sign:
                return FloatUtils._double_neg_infinity if is_double else FloatUtils._float_neg_infinity
            else:
                return FloatUtils._double_infinity if is_double else FloatUtils._float_infinity
        elif exponent < min_exponent:
            return FloatUtils._double_zero if is_double else FloatUtils._float_zero

        # calculate the result
        if is_double:
            high = 0
            for i in range(20):
                first_bit += 1
                high = (high << 1) | buffer[first_bit]

            low = 0
            for i in range(20, 52):
                first_bit += 1
                low = (low << 1) | buffer[first_bit]

            high |= (exponent + bias) << 20
            high = (sign << 31) | (high & 0x7FFFFFFF)

            res_array = [
                low & 0xFF,
                (low >> 8) & 0xFF,
                (low >> 16) & 0xFF,
                low >> 24,
                high & 0xFF,
                (high >> 8) & 0xFF,
                (high >> 16) & 0xFF,
                high >> 24
            ]
            return res_array
        else:
            result = 0
            for i in range(23):
                first_bit += 1
                result = (result << 1) | buffer[first_bit]

            result |= (exponent + bias) << 23
            result = (sign << 31) | (result & 0x7FFFFFFF)

            res_array = [
                result & 0xFF,
                (result >> 8) & 0xFF,
                (result >> 16) & 0xFF,
                result >> 24
            ]
            return res_array

    @staticmethod
    def convert_array_to_number(buffer, is_double):
        """Convert an array of bytes to a Python float"""
        exponent_bits = 11 if is_double else 8
        bias = (1 << (exponent_bits - 1)) - 1
        sign = (buffer[7 if is_double else 3] & 0x80) != 0
        
        exponent = (((buffer[7] & 0x7F) << 4) | ((buffer[6] & 0xF0) >> 4)) if is_double else \
                   (((buffer[3] & 0x7F) << 1) | ((buffer[2] & 0x80) >> 7))

        # check if the buffer is valid
        if exponent == 0xFF:
            raise BondException("Not a valid float/double buffer.")

        res = 1
        e = 1
        if is_double:
            high = ((buffer[6] & 0xF) << 28) | ((buffer[5] & 0xFF) << 20) | ((buffer[4] & 0xFF) << 12)
            low = (buffer[3] << 24) | ((buffer[2] & 0xFF) << 16) | ((buffer[1] & 0xFF) << 8) | (buffer[0] & 0xFF)
            if not exponent and not high and not low:
                return 0.0
            for i in range(20):
                e /= 2
                if high < 0:
                    res += e
                high <<= 1
            for i in range(32):
                e /= 2
                if low < 0:
                    res += e
                low <<= 1
        else:
            data = ((buffer[2] & 0x7F) << 25) | ((buffer[1] & 0xFF) << 17) | ((buffer[0] & 0xFF) << 9)
            if not exponent and not data:
                return 0.0
            for i in range(23):
                e /= 2
                if data < 0:
                    res += e
                data <<= 1

        res *= 2 ** (exponent - bias)
        return -res if sign else res
