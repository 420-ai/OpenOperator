from typing import Tuple
from ...bond.bond_const import BondDataType
from ...bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from ...models.user import User

def deserialize_user(reader: IProtocolReader) -> dict:
    """
    Deserialize a User object from the protocol reader.
    Returns a dictionary containing 'status' (bool) and 'user' (User).
    """
    local_user = User()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
         
        if field_begin["result"] == False:
            Logger.log_error("Error deserializing user, can't find field begin")
            return {"status": False, "user": local_user}
        
        if (field_begin["type"] == BondDataType.BT_STOP or 
            field_begin["type"] == BondDataType.BT_STOP_BASE):
            break
            
        if field_begin["id"] == 1:
            local_user.id = reader.read_string()
        elif field_begin["id"] == 2:
            local_user.local_id = reader.read_string()
        elif field_begin["id"] == 3:
            local_user.auth_id = reader.read_string()
        elif field_begin["id"] == 4:
            local_user.locale = reader.read_string()
        else:
            Logger.log_error(f"Error deserializing user, unknown type {field_begin['id']}")
            return {"status": False, "user": local_user}
            
        reader.read_field_end()

    return {"status": True, "user": local_user}
