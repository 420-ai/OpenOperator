from typing import List, Union
from bond.microsoft_bond import CompactBinaryProtocolReader
from .client_to_collector_request import ClientToCollectorRequest
from models.cs_record import CsRecord

def decode_kusto_request(request: Union[bytes, List[int]]) -> List[CsRecord]:
    records: List[CsRecord] = []
    binary_records = request.split(b"\x03\51\46")
    for binary_record_bytes in binary_records:
        if len(binary_record_bytes) > 0:
            compact_binary_protocol_reader = CompactBinaryProtocolReader()
            compact_binary_protocol_reader.set_data(binary_record_bytes)
            
            record = ClientToCollectorRequest.deserialize_record(compact_binary_protocol_reader)
            
            if record["status"]:
                records.append(record["record"])
    
    return records
