from typing import List
from .attribute import Attribute
from .enums import ValueKind

class Value:
    def __init__(self):
        # 1: optional ValueKind type
        self.type: ValueKind = ValueKind.VALUE_STRING
        # 2: optional vector<Attributes> attributes
        self.attributes: List[Attribute] = []
        # 3: optional string stringValue
        self.string_value: str = ""
        # 4: optional int64 longValue
        self.long_value: int = 0
        # 5: optional double doubleValue
        self.double_value: float = 0.0
        # 6: optional vector<vector<uint8>> guidValue
        self.guid_value: List[List[int]] = []
        # 10: optional vector<vector<string>> stringArray
        self.string_array: List[List[str]] = []
        # 11: optional vector<vector<int64>> longArray
        self.long_array: List[List[int]] = []
        # 12: optional vector<vector<double>> doubleArray
        self.double_array: List[List[float]] = []
        # 13: optional vector<vector<vector<uint8>>> guidArray
        self.guid_array: List[List[List[int]]] = []

    def to_json(self):
        if self.type == ValueKind.VALUE_STRING:
            return self.string_value
        elif self.type == ValueKind.VALUE_ARRAY_STRING:
            return str(self.string_array)
        elif self.type == ValueKind.VALUE_DOUBLE:
            return str(self.double_value)
        elif self.type == ValueKind.VALUE_ARRAY_DOUBLE:
            return str(self.double_array)
        elif self.type in (ValueKind.VALUE_INT32, ValueKind.VALUE_INT64, 
                          ValueKind.VALUE_UINT32, ValueKind.VALUE_UINT64):
            return str(self.long_value)
        elif self.type in (ValueKind.VALUE_ARRAY_INT32, ValueKind.VALUE_ARRAY_INT64,
                          ValueKind.VALUE_ARRAY_UINT32, ValueKind.VALUE_ARRAY_UINT64):
            return str(self.long_array)
        elif self.type == ValueKind.VALUE_GUID:
            return str(self.guid_value)
        elif self.type == ValueKind.VALUE_ARRAY_GUID:
            return str(self.guid_array)
        else:
            return self.string_value

    def __str__(self) -> str:
        return self.to_json()
