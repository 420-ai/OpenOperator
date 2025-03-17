from typing import Tuple
from ...bond.bond_const import BondDataType
from ...bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from ...models.utc import Utc

def deserialize_utc(reader: IProtocolReader) -> dict:
    """
    Deserialize a Utc object from the protocol reader.
    Returns a dictionary containing 'status' (bool) and 'utc' (Utc).
    """
    local_utc = Utc()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log_error("Error deserializing Utc, can't find field begin")
            return {"status": False, "utc": local_utc}
        
        if (field_begin["type"] == BondDataType.BT_STOP or 
            field_begin["type"] == BondDataType.BT_STOP_BASE):
            break
            
        if field_begin["id"] == 1:
            local_utc.st_id = reader.read_string()
        elif field_begin["id"] == 2:
            local_utc.a_id = reader.read_string()
        elif field_begin["id"] == 3:
            local_utc.ra_id = reader.read_string()
        elif field_begin["id"] == 4:
            local_utc.op = reader.read_string()
        elif field_begin["id"] == 5:
            local_utc.cat = reader.read_int64_to_number()
        elif field_begin["id"] == 6:
            local_utc.flags = reader.read_int64_to_number()
        elif field_begin["id"] == 7:
            local_utc.sqm_id = reader.read_string()
        elif field_begin["id"] == 9:
            local_utc.mon = reader.read_string()
        elif field_begin["id"] == 10:
            local_utc.cp_id = reader.read_int32()
        elif field_begin["id"] == 11:
            local_utc.b_seq = reader.read_string()
        elif field_begin["id"] == 12:
            local_utc.epoch = reader.read_string()
        elif field_begin["id"] == 13:
            local_utc.seq = reader.read_int64_to_number()
        elif field_begin["id"] == 14:
            local_utc.pop_sample = reader.read_double()
        elif field_begin["id"] == 15:
            local_utc.event_flags = reader.read_int64_to_number()
        else:
            Logger.log_error(f"Error deserializing utc, unknown type {field_begin['id']}")
            return {"status": False, "utc": local_utc}
            
        reader.read_field_end()

    return {"status": True, "utc": local_utc}
