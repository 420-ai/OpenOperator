"""
microsoft_bond_decoding.py
Copyright: Microsoft 2016
"""
import struct
from bond.microsoft_bond_utils import EnvironmentChecker
from bond.microsoft_bond_primitives import Int64, UInt64

class Utf8:
    @staticmethod
    def get_string(data):
        """Convert UTF-8 bytes to string"""
        # Convert the list of integers to bytes
        byte_array = bytes(data)
        return byte_array.decode('utf-8')


class Base64:
    @staticmethod
    def get_bytes(base64_str):
        """Convert a base64 string to bytes"""
        import base64
        decoded = base64.b64decode(base64_str)
        return list(decoded)


class Varint:
    @staticmethod
    def get_int64(buffer):
        """Decode a varint to Int64"""
        int64 = Int64("0")
        data = Varint._read(buffer)
        int64.low = data[0]
        if len(data) > 1:
            int64.high = data[1]
        return int64

    @staticmethod
    def get_number(buffer):
        """Decode a varint to a number"""
        return Varint._read(buffer)[0]

    @staticmethod
    def _read(buffer):
        """Read a varint from a buffer"""
        result = []
        tmp = 0
        has_more = True
        read_bits = 0

        # First, try to read the first 32 bits
        while has_more:
            raw = buffer.pop(0) if buffer else 0
            has_more = (raw & 0x80) != 0
            raw = raw & 0x7F
            if read_bits < 28:
                tmp |= raw << read_bits
                read_bits += 7
            else:
                # Only lower 4 bits can be put
                tmp |= raw << read_bits
                result.append(tmp)
                tmp = raw >> 4
                read_bits = 3
                break

        # Then, read the second 32 bits
        while has_more:
            raw = buffer.pop(0) if buffer else 0
            has_more = (raw & 0x80) != 0
            raw = raw & 0x7F
            tmp |= raw << read_bits
            read_bits += 7
            if read_bits >= 32:
                break
        
        result.append(tmp)
        return result


class Float:
    @staticmethod
    def get_number(buffer):
        """Convert bytes to float"""
        if EnvironmentChecker.is_binary_support():
            byte_array = bytes(buffer[:4])
            return struct.unpack("<f", byte_array)[0]
        else:
            from .microsoft_bond_floatutils import FloatUtils
            return FloatUtils.convert_array_to_number(buffer, False)


class Double:
    @staticmethod
    def get_number(buffer):
        """Convert bytes to double"""
        if EnvironmentChecker.is_binary_support():
            byte_array = bytes(buffer[:8])
            return struct.unpack("<d", byte_array)[0]
        else:
            from .microsoft_bond_floatutils import FloatUtils
            return FloatUtils.convert_array_to_number(buffer, True)


class Zigzag:
    @staticmethod
    def decode_zigzag16(value):
        """Decode a 16-bit zigzagged integer"""
        return ((((0xFFFF & value) >> 1) ^ (-(value & 1))) << 16) >> 16

    @staticmethod
    def decode_zigzag32(value):
        """Decode a 32-bit zigzagged integer"""
        return (value >> 1) ^ (-(value & 1))

    @staticmethod
    def decode_zigzag64(value):
        """Decode a 64-bit zigzagged integer"""
        # (value >>> 1) ^ (-(value & 1))
        tmp_h = value.high & 1
        high = value.high >> 1
        tmp_l = value.low & 1
        low = value.low >> 1
        low = (tmp_h << 31) | low
        if tmp_l:
            low ^= 0xFFFFFFFF
            high ^= 0xFFFFFFFF

        res = UInt64("0")
        res.low = low
        res.high = high
        return res
