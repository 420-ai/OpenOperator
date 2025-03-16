from typing import List, Union
from bond.microsoft_bond import CompactBinaryProtocolReader
from .client_to_collector_request import ClientToCollectorRequest
from models.cs_record import CsRecord

def decode_kusto_request(request: Union[bytes, List[int]]) -> List[CsRecord]:
    v: List[CsRecord] = []
    i: int = 0
    length: int = 0

    while i < len(request):
        length = len(request) - 1
        tmp_array = request[i : i + length]
        j: int = 3
        found: bool = False

        while j < length and len(tmp_array) > j + 2:
            # Skip to the next occurrence of 0x3
            while j < length and tmp_array[j] != 0x3:
                j += 1

            # Check if we are within bounds
            if j < length:
                if j + 2 < length:
                    # 51 == '3'
                    # 46 == '.'
                    if tmp_array[j + 1] == 51 and tmp_array[j + 2] == 46:
                        found = True
                        break
                j += 1

        if not found:
            j += 1

        input_data = request[i : i + j]

        compact_binary_protocol_reader = CompactBinaryProtocolReader()
        compact_binary_protocol_reader.set_data(input_data)

        record = ClientToCollectorRequest.deserialize_record(
            compact_binary_protocol_reader
        )

        i += j - 1
        if record["status"]:
            v.append(record["record"])

    return v
