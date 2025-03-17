from ...bond.bond_const import BondDataType
from ...bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from ...models.app import App

def deserialize_app(reader: IProtocolReader) -> dict:
    """
    Deserialize an App object from the protocol reader
    
    Returns:
        dict: Contains 'status' (bool) and 'app' (App)
    """
    local_app = App()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if not field_begin["result"]:
            Logger.log_error("Error deserializing app, can't find field begin")
            return {"status": False, "app": local_app}
            
        if (field_begin["type"] == BondDataType.BT_STOP or 
                field_begin["type"] == BondDataType.BT_STOP_BASE):
            break
            
        if field_begin["id"] == 1:
            local_app.exp_id = reader.read_string()
            
        elif field_begin["id"] == 2:
            local_app.user_id = reader.read_string()
            
        elif field_begin["id"] == 3:
            local_app.env = reader.read_string()
            
        elif field_begin["id"] == 4:
            local_app.as_id = reader.read_int32()
            
        elif field_begin["id"] == 5:
            local_app.id = reader.read_string()
            
        elif field_begin["id"] == 6:
            local_app.ver = reader.read_string()
            
        elif field_begin["id"] == 7:
            local_app.locale = reader.read_string()
            
        elif field_begin["id"] == 8:
            local_app.name = reader.read_string()
            
        else:
            Logger.log_error(f"Error deserializing app, unknown type {field_begin['id']}")
            return {"status": False, "app": local_app}
            
        reader.read_field_end()
        
    return {"status": True, "app": local_app}
