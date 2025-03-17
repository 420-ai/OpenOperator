from typing import Tuple
from ...bond.bond_const import BondDataType
from ...bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from ...models.enums import PIIKind

def deserialize_pii(reader: IProtocolReader) -> dict:
    """
    Deserialize a PIIKind enum from the protocol reader.
    Returns a dictionary containing 'status' (bool) and 'pii' (PIIKind).
    """
    local_pii = PIIKind.NotSet
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log_error("Error deserializing pii, can't find field begin")
            return {"status": False, "pii": local_pii}
        
        if (field_begin["type"] == BondDataType.BT_STOP or 
            field_begin["type"] == BondDataType.BT_STOP_BASE):
            break
            
        if field_begin["id"] == 1:
            local_pii = PIIKind(reader.read_int32())
        else:
            Logger.log_error(
                f"Error deserializing pii, unknown type {field_begin['id']}"
            )
            return {"status": False, "pii": local_pii}
            
        reader.read_field_end()

    return {"status": True, "pii": local_pii}
