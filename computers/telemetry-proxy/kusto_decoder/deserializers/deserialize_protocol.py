from typing import Tuple
from bond.microsoft_bond import BondDataType, IProtocolReader
from ..utils.logger import Logger
from models.protocol import Protocol

def deserialize_protocol(reader: IProtocolReader) -> dict:
    """
    Deserialize a Protocol object from the protocol reader.
    Returns a dictionary containing 'status' (bool) and 'protocol' (Protocol).
    """
    local_protocol = Protocol()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if not field_begin["result"]:
            Logger.log_error("Error Deserializing Protocol, cant find begin field")
            return {"status": False, "protocol": local_protocol}
        
        if (field_begin["type"] == BondDataType.BT_STOP or 
            field_begin["type"] == BondDataType.BT_STOP_BASE):
            break
            
        if field_begin["id"] == 1:
            local_protocol.metadata_crc = reader.read_int32()
        elif field_begin["id"] == 2:
            container_data = reader.read_container_begin()
            if container_data["element_type"] != BondDataType.BT_LIST:
                Logger.log_error(
                    f"Error deserializing protocol, wrong container type for ticket_keys, expected list found {container_data['element_type']}"
                )
                return {"status": False, "protocol": local_protocol}
                
            for _ in range(container_data["size"]):
                internal_container = reader.read_container_begin()
                if internal_container["element_type"] != BondDataType.BT_STRING:
                    Logger.log_error(
                        f"Error deserializing protocol, wrong container type for ticket_keys element, expected string found {internal_container['element_type']}"
                    )
                    return {"status": False, "protocol": local_protocol}
                    
                tickets = []
                for _ in range(internal_container["size"]):
                    tickets.append(reader.read_string())
                    
                reader.read_container_end()
                local_protocol.ticket_keys.append(tickets)
                
            reader.read_container_end()
        elif field_begin["id"] == 3:
            local_protocol.dev_make = reader.read_string()
        elif field_begin["id"] == 4:
            local_protocol.dev_model = reader.read_string()
        else:
            Logger.log_error(
                f"Error deserializing protocol, unknown type {field_begin['id']}"
            )
            return {"status": False, "protocol": local_protocol}
            
        reader.read_field_end()
        
    return {"status": True, "protocol": local_protocol}
