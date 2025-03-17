"""
microsoft_bond_encoding.py
Copyright: Microsoft 2016
"""
from .microsoft_bond_primitives import UInt64, Number
from .microsoft_bond_utils import EnvironmentChecker
import struct

class Utf8:
    @staticmethod
    def get_bytes(value):
        """Convert a string to UTF-8 bytes"""
        return list(value.encode('utf-8'))


class Base64:
    @staticmethod
    def get_string(in_array):
        """Convert binary data to a base64 string"""
        import base64
        # Convert the list of integers to bytes
        byte_array = bytes(in_array)
        # Convert to base64
        return base64.b64encode(byte_array).decode('ascii')


class Varint:
    @staticmethod
    def get_bytes(value):
        """Encode an integer as varint"""
        array = []
        while value & 0xFFFFFF80:
            array.append((value & 0x7F) | 0x80)
            value = value >> 7
        array.append(value & 0x7F)
        return array


class Varint64:
    @staticmethod
    def get_bytes(value):
        """Encode a 64-bit integer as varint"""
        low = value.low
        high = value.high
        array = []
        while high or 0xFFFFFF80 & low:
            array.append((low & 0x7F) | 0x80)
            low = ((high & 0x7F) << 25) | (low >> 7)
            high >>= 7
        array.append(low & 0x7F)
        return array


class Float:
    @staticmethod
    def get_bytes(value):
        """Convert a float to bytes"""
        if EnvironmentChecker.is_binary_support():
            return list(struct.pack("<f", value))
        else:
            from .microsoft_bond_floatutils import FloatUtils
            return FloatUtils.convert_number_to_array(value, False)


class Double:
    @staticmethod
    def get_bytes(value):
        """Convert a double to bytes"""
        if EnvironmentChecker.is_binary_support():
            return list(struct.pack("<d", value))
        else:
            from .microsoft_bond_floatutils import FloatUtils
            return FloatUtils.convert_number_to_array(value, True)


class Zigzag:
    @staticmethod
    def encode_zigzag16(value):
        """Encode a 16-bit signed integer using zigzag encoding"""
        value = Number.to_int16(value)
        return (value << 1) ^ (value >> (2 * 8 - 1))

    @staticmethod
    def encode_zigzag32(value):
        """Encode a 32-bit signed integer using zigzag encoding"""
        value = Number.to_int32(value)
        return (value << 1) ^ (value >> (4 * 8 - 1))

    @staticmethod
    def encode_zigzag64(value):
        """Encode a 64-bit signed integer using zigzag encoding"""
        low = value.low
        high = value.high
        tmp_h = (high << 1) | (low >> 31)
        tmp_l = low << 1
        if high & 0x80000000:
            tmp_h = ~tmp_h
            tmp_l = ~tmp_l

        res = UInt64("0")
        res.low = tmp_l
        res.high = tmp_h
        return res
