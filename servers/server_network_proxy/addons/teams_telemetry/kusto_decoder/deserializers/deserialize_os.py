from typing import Tuple
from ...bond.bond_const import BondDataType
from ...bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from ...models.os import Os

def deserialize_os(reader: IProtocolReader) -> dict:
    """
    Deserialize an Os object from the protocol reader.
    Returns a dictionary containing 'status' (bool) and 'os' (Os).
    """
    local_os = Os()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log_error("Error deserializing Os, can't find field begin")
            return {"status": False, "os": local_os}
        
        if (field_begin["type"] == BondDataType.BT_STOP or 
            field_begin["type"] == BondDataType.BT_STOP_BASE):
            break
            
        if field_begin["id"] == 1:
            local_os.locale = reader.read_string()
        elif field_begin["id"] == 2:
            local_os.exp_id = reader.read_string()
        elif field_begin["id"] == 3:
            local_os.boot_id = reader.read_int32()
        elif field_begin["id"] == 4:
            local_os.name = reader.read_string()
        elif field_begin["id"] == 5:
            local_os.ver = reader.read_string()
        else:
            Logger.log_error(
                f"Error deserializing os, unknown type {field_begin['id']}"
            )
            return {"status": False, "os": local_os}
            
        reader.read_field_end()

    return {"status": True, "os": local_os}
