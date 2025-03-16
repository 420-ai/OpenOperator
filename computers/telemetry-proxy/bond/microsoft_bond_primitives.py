"""
microsoft_bond_primitives.py
Copyright: Microsoft 2016
"""

class Int64:
    """Represents a signed 64-bit integer"""
    def __init__(self, number_str):
        self.low = 0
        self.high = 0
        value = int(number_str)
        self.low = value & 0xFFFFFFFF
        self.high = (value >> 32) & 0xFFFFFFFF
        if value < 0 and self.high == 0:
            self.high = -1

    def equals(self, number_str):
        tmp = Int64(number_str)
        return self.low == tmp.low and self.high == tmp.high


class UInt64:
    """Represents an unsigned 64-bit integer"""
    def __init__(self, number_str):
        self.low = 0
        self.high = 0
        value = int(number_str)
        self.low = value & 0xFFFFFFFF
        self.high = (value >> 32) & 0xFFFFFFFF

    def equals(self, number_str):
        tmp = UInt64(number_str)
        return self.low == tmp.low and self.high == tmp.high


class Number:
    """Number conversion utilities"""
    @staticmethod
    def to_byte(value):
        return Number.to_uint8(value)

    @staticmethod
    def to_int8(value):
        sign_mask = ((value & 0x80) << 24) >> 24
        return (value & 0x7F) | sign_mask

    @staticmethod
    def to_int16(value):
        sign_mask = ((value & 0x8000) << 16) >> 16
        return (value & 0x7FFF) | sign_mask

    @staticmethod
    def to_int32(value):
        sign_mask = value & 0x80000000
        return (value & 0x7FFFFFFF) | sign_mask

    @staticmethod
    def to_uint8(value):
        return value & 0xFF

    @staticmethod
    def to_uint16(value):
        return value & 0xFFFF

    @staticmethod
    def to_uint32(value):
        return value & 0xFFFFFFFF
