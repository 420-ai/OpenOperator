"""
microsoft_bond.py
Copyright: Microsoft 2016
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, TypeVar, Generic, Union
from ..bond.bond_const import BondDataType
from . import microsoft_bond_decoding as Decoding
from ..bond.microsoft_bond_primitives import Int64, UInt64, Number
from logging import getLogger

logger = getLogger("BondLogger")

T = TypeVar('T')

class Bonded(Generic[T]):
    """Generic Bond container class"""
    pass


class IBondSerializable(ABC):
    """Interface for serializable Bond objects"""
    
    @abstractmethod
    def write(self, writer: 'IProtocolWriter') -> None:
        """Write object to protocol writer"""
        pass
    
    @abstractmethod
    def read(self, reader: 'IProtocolReader') -> None:
        """Read object from protocol reader"""
        pass


class IProtocolWriter(ABC):
    """
    Declares the interface to be implemented by a protocol in order to
    serialize Bond data.
    """
    
    @abstractmethod
    def write_blob(self, blob: List[int]) -> None:
        pass
    
    @abstractmethod
    def write_bool(self, value: bool) -> None:
        pass
    
    @abstractmethod
    def write_container_begin(self, size: int, element_type: BondDataType) -> None:
        pass
    
    @abstractmethod
    def write_map_container_begin(self, size: int, key_type: BondDataType, value_type: BondDataType) -> None:
        pass
    
    @abstractmethod
    def write_container_end(self) -> None:
        pass
    
    @abstractmethod
    def write_double(self, value: float) -> None:
        pass
    
    @abstractmethod
    def write_float(self, value: float) -> None:
        pass
    
    @abstractmethod
    def write_field_begin(self, type_: BondDataType, id_: int, metadata: IBondSerializable) -> None:
        pass
    
    @abstractmethod
    def write_field_end(self) -> None:
        pass
    
    @abstractmethod
    def write_field_omitted(self, type_: BondDataType, id_: int, metadata: IBondSerializable) -> None:
        pass
    
    @abstractmethod
    def write_int16(self, value: int) -> None:
        pass
    
    @abstractmethod
    def write_int32(self, value: int) -> None:
        pass
    
    @abstractmethod
    def write_int64(self, value: Int64) -> None:
        pass
    
    @abstractmethod
    def write_int8(self, value: int) -> None:
        pass
    
    @abstractmethod
    def write_string(self, value: str) -> None:
        pass
    
    @abstractmethod
    def write_struct_begin(self, metadata: IBondSerializable, is_base: bool) -> None:
        pass
    
    @abstractmethod
    def write_struct_end(self, is_base: bool) -> None:
        pass
    
    @abstractmethod
    def write_uint16(self, value: int) -> None:
        pass
    
    @abstractmethod
    def write_uint32(self, value: int) -> None:
        pass
    
    @abstractmethod
    def write_uint64(self, value: UInt64) -> None:
        pass
    
    @abstractmethod
    def write_uint8(self, value: int) -> None:
        pass
    
    @abstractmethod
    def write_wstring(self, value: str) -> None:
        pass


class IProtocolReader(ABC):
    """Interface for protocol readers"""
    
    @abstractmethod
    def read_blob(self) -> List[int]:
        pass
    
    @abstractmethod
    def read_bool(self) -> bool:
        pass
    
    @abstractmethod
    def read_container_begin(self) -> Dict[str, Any]:
        """Returns a dict with 'size' and 'elementType'"""
        pass
    
    @abstractmethod
    def read_map_container_begin(self) -> Dict[str, Any]:
        """Returns a dict with 'size', 'keyType', and 'valueType'"""
        pass
    
    @abstractmethod
    def read_container_end(self) -> Any:
        pass
    
    @abstractmethod
    def read_double(self) -> float:
        pass
    
    @abstractmethod
    def read_float(self) -> float:
        pass
    
    @abstractmethod
    def is_begin_with_field_of_id(self, id_: int) -> bool:
        pass
    
    @abstractmethod
    def read_field_begin(self, id_: int) -> None:
        pass
    
    @abstractmethod
    def read_field_begin_unknown(self) -> Dict[str, Any]:
        """Returns a dict with 'result', 'type', and 'id'"""
        pass
    
    @abstractmethod
    def read_field_end(self) -> None:
        pass
    
    @abstractmethod
    def read_field_omitted(self) -> None:
        pass
    
    @abstractmethod
    def read_int16(self) -> int:
        pass
    
    @abstractmethod
    def read_int32(self) -> int:
        pass
    
    @abstractmethod
    def read_int64(self) -> Int64:
        pass
    
    @abstractmethod
    def read_int64_to_number(self) -> int:
        pass
    
    @abstractmethod
    def read_int8(self) -> int:
        pass
    
    @abstractmethod
    def read_string(self) -> str:
        pass
    
    @abstractmethod
    def read_struct_begin(self) -> None:
        pass
    
    @abstractmethod
    def read_struct_end(self) -> BondDataType:
        pass
    
    @abstractmethod
    def read_uint16(self) -> int:
        pass
    
    @abstractmethod
    def read_uint32(self) -> int:
        pass
    
    @abstractmethod
    def read_uint64(self) -> UInt64:
        pass
    
    @abstractmethod
    def read_uint64_to_number(self) -> int:
        pass
    
    @abstractmethod
    def read_uint8(self) -> int:
        pass
    
    @abstractmethod
    def read_wstring(self) -> str:
        pass
    
    @abstractmethod
    def set_data(self, buf: Union[bytes, List[int]]) -> None:
        pass


class CompactBinaryProtocolReader(IProtocolReader):
    """Implementation of CompactBinaryProtocolReader"""
    
    def __init__(self):
        self.data = []
    
    def set_data(self, buf: bytes | List[int]) -> None:
        if isinstance(buf, bytes):
            self.data = list(buf)
        else:
            self.data = buf
    
    def read_blob(self) -> List[int]:
        raise NotImplementedError("not implemented")
    
    def read_bool(self) -> bool:
        b = self.read_byte()
        return b == 1
    
    def read_container_begin(self) -> Dict[str, Any]:
        element_type = BondDataType(self.read_uint8())
        size = self.read_uint32()
        return {"elementType": element_type, "size": size}
    
    def read_map_container_begin(self) -> Dict[str, Any]:
        key_type = self.read_uint8()
        value_type = self.read_uint8()
        size = self.read_uint32()
        return {"size": size, "keyType": key_type, "valueType": value_type}
    
    def read_container_end(self) -> Any:
        return None
    
    def read_double(self) -> float:
        bytes_data = self.data[:8]
        del self.data[:8]
        return Decoding.Double.get_number(bytes_data)
    
    def read_float(self) -> float:
        bytes_data = self.data[:4]
        del self.data[:4]
        return Decoding.Float.get_number(bytes_data)
    
    def is_begin_with_field_of_id(self, id_: int) -> bool:
        if id_ <= 5:
            byte = self.peek_byte(1)[0]
            return ((byte >> 5) & 0x3) > 0
        elif id_ <= 0xff:
            byte = self.peek_byte(2)[1]
            return byte == id_
        else:
            byte = self.peek_byte(3)
            low = byte[1]
            high = byte[2] << 8
            id_read = high + low
            return id_read == id_
    
    def read_field_begin(self, id_: int) -> None:
        if id_ <= 5:
            self.read_byte()
        elif id_ <= 0xff:
            self.read_byte()
            self.read_byte()
        else:
            self.read_byte()
            self.read_byte()
            self.read_byte()
    
    def read_field_begin_unknown(self) -> Dict[str, Any]:
        local_type = 0
        local_id = 0
        try:
            self.peek_byte(1)
            raw = self.read_uint8()           
            local_type = raw & 31
            raw >>= 5
            if raw <= 5:
                local_id = raw
            elif raw == 6:
                self.peek_byte(1)
                local_id = self.read_uint8()
            elif raw == 7:
                self.peek_byte(2)
                raw = self.read_uint8()
                raw2 = self.read_uint8()
                local_id = raw | (raw2 << 8)
        except Exception as e:
            logger.error(f"Error reading begin field section: {e}")
            return {"result": False, "type": 0, "id": 0}
        
        return {"result": True, "type": local_type, "id": local_id}
    
    def read_field_end(self) -> None:
        return None
    
    def read_field_omitted(self) -> None:
        return None
    
    def read_int16(self) -> int:
        n = self.read_uint16()
        return Decoding.Zigzag.decode_zigzag16(n)
    
    def read_int32(self) -> int:
        n = self.read_uint32()
        return Decoding.Zigzag.decode_zigzag32(n)
    
    def read_int64(self) -> Int64:
        u64 = self.read_uint64()
        i64 = Decoding.Zigzag.decode_zigzag64(u64)
        return i64
    
    def read_int64_to_number(self) -> int:
        i64 = self.read_int64()
        return i64.high * 0x100000000 + i64.low
    
    def read_int8(self) -> int:
        return Number.to_int8(self.read_byte())
    
    def read_string(self) -> str:
        length = self.read_uint32()
        if length == 0:
            return ""
        else:
            bytes_data = self.data[:length]
            del self.data[:length]
            return Decoding.Utf8.get_string(bytes_data)
    
    def read_struct_begin(self) -> None:
        return None
    
    def read_struct_end(self) -> BondDataType:
        return self.read_uint8()
    
    def read_uint16(self) -> int:
        return Decoding.Varint.get_number(self.data)
    
    def read_uint32(self) -> int:
        return Decoding.Varint.get_number(self.data)
    
    def read_uint64(self) -> UInt64:
        return Decoding.Varint.get_int64(self.data)
    
    def read_uint64_to_number(self) -> int:
        u64 = self.read_uint64()
        if u64.low < 0:
            a = u64.low & 0x7fffffff
            b = 0x80000000
            u64.low = a + b
        return u64.high * 0x100000000 + u64.low
    
    def read_uint8(self) -> int:
        return self.read_byte()
    
    def read_wstring(self) -> str:
        result = ""
        length = self.read_uint32()
        for _ in range(length):
            low = self.read_byte()
            high = self.read_byte() << 8
            char_code = high + low
            result += chr(char_code)
        return result
    
    def read_byte(self) -> int:
        if not self.data:
            return 0
        return self.data.pop(0)
    
    def peek_byte(self, num_byte: int = 1) -> List[int]:
        if len(self.data) < num_byte:
            raise ValueError(f"not enough bytes {len(self.data)} - {num_byte}")
        return self.data[:num_byte]
