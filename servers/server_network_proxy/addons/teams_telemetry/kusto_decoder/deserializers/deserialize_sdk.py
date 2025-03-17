from typing import Tuple
from ...bond.microsoft_bond import BondDataType, IProtocolReader
from ..utils.logger import Logger
from ...models.sdk import Sdk

def deserialize_sdk(reader: IProtocolReader) -> dict:
    """
    Deserialize an Sdk object from the protocol reader.
    Returns a dictionary containing 'status' (bool) and 'sdk' (Sdk).
    """
    local_sdk = Sdk()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log("Error deserializing SDK, can not detect begin")
            return {"status": False, "sdk": local_sdk}
        
        if (field_begin["type"] == BondDataType.BT_STOP or 
            field_begin["type"] == BondDataType.BT_STOP_BASE):
            break
            
        if field_begin["id"] == 1:
            local_sdk.lib_ver = reader.read_string()
        elif field_begin["id"] == 2:
            local_sdk.epoch = reader.read_string()
        elif field_begin["id"] == 3:
            local_sdk.seq = reader.read_int64_to_number()
        elif field_begin["id"] == 4:
            local_sdk.install_id = reader.read_string()
        else:
            Logger.log(f"Error deserializing SDK, unknown type {field_begin['id']}")
            return {"status": False, "sdk": local_sdk}
            
        reader.read_field_end()

    return {"status": True, "sdk": local_sdk}
