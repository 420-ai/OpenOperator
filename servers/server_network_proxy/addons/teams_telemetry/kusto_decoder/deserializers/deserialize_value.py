from ...bond.bond_const import BondDataType
from ...bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from ...models.value import Value
from ...models.enums import ValueKind
from .deserialize_attribute import deserialize_attribute

def deserialize_value(reader: IProtocolReader) -> dict:
    """
    Deserialize a Value object from the protocol reader
    
    Returns:
        dict: Contains 'status' (bool) and 'value' (Value)
    """
    local_value = Value()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if not field_begin["result"]:
            Logger.log_error("Error deserializing value, can't find field begin")
            return {"status": False, "value": local_value}
        
        if (field_begin["type"] == BondDataType.BT_STOP or 
                field_begin["type"] == BondDataType.BT_STOP_BASE):
            break
            
        if field_begin["id"] == 1:
            local_value.type = ValueKind(reader.read_int32())
            
        elif field_begin["id"] == 2:
            local_container = reader.read_container_begin()
            if local_container["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing value, wrong container type for attribute expected struct found {local_container['elementType']}"
                )
                return {"status": False, "value": local_value}
                
            for _ in range(local_container["size"]):
                attribute = deserialize_attribute(reader)
                if not attribute["status"]:
                    Logger.log_error("Error deserializing value, error getting attribute")
                    return {"status": False, "value": local_value}
                local_value.attributes.append(attribute["attribute"])
                
            reader.read_container_end()
            
        elif field_begin["id"] == 3:
            local_value.string_value = reader.read_string()
            
        elif field_begin["id"] == 4:
            local_value.long_value = reader.read_int64_to_number()
            
        elif field_begin["id"] == 5:
            local_value.double_value = reader.read_double()
            
        elif field_begin["id"] == 6:
            local_container = reader.read_container_begin()
            if local_container["elementType"] != BondDataType.BT_LIST:
                Logger.log_error(
                    f"Error deserializing value, wrong container type for guidValue, expected list found {local_container['elementType']}"
                )
                return {"status": False, "value": local_value}
                
            for _ in range(local_container["size"]):
                internal_guid_container = reader.read_container_begin()
                if internal_guid_container["elementType"] != BondDataType.BT_UINT8:
                    Logger.log_error(
                        f"Error deserializing value, wrong container type for guid element, expected int8 found {internal_guid_container['elementType']}"
                    )
                    return {"status": False, "value": local_value}
                    
                local_guids = []
                for _ in range(internal_guid_container["size"]):
                    local_guids.append(reader.read_uint8())
                    
                local_value.guid_value.append(local_guids)
                reader.read_container_end()
                
            reader.read_container_end()
            
        elif field_begin["id"] == 10:
            local_container = reader.read_container_begin()
            if local_container["elementType"] != BondDataType.BT_LIST:
                Logger.log_error(
                    f"Error deserializing value, wrong container type for stringArray, expected list found {local_container['elementType']}"
                )
                return {"status": False, "value": local_value}
                
            for _ in range(local_container["size"]):
                internal_string_container = reader.read_container_begin()
                if internal_string_container["elementType"] != BondDataType.BT_STRING:
                    Logger.log_error(
                        f"Error deserializing value, wrong container type for stringArray element, expected string found {internal_string_container['elementType']}"
                    )
                    return {"status": False, "value": local_value}
                    
                local_strings = []
                for _ in range(internal_string_container["size"]):
                    local_strings.append(reader.read_string())
                    
                local_value.string_array.append(local_strings)
                reader.read_container_end()
                
            reader.read_container_end()
            
        elif field_begin["id"] == 11:
            local_container = reader.read_container_begin()
            if local_container["elementType"] != BondDataType.BT_LIST:
                Logger.log_error(
                    f"Error deserializing value, wrong container type for longArray, expected list found {local_container['elementType']}"
                )
                return {"status": False, "value": local_value}
                
            for _ in range(local_container["size"]):
                internal_long_container = reader.read_container_begin()
                if internal_long_container["elementType"] != BondDataType.BT_INT64:
                    Logger.log_error(
                        f"Error deserializing value, wrong container type for longArray element, expected int64 found {internal_long_container['elementType']}"
                    )
                    return {"status": False, "value": local_value}
                    
                local_longs = []
                for _ in range(internal_long_container["size"]):
                    local_longs.append(reader.read_int64_to_number())
                    
                local_value.long_array.append(local_longs)
                reader.read_container_end()
                
            reader.read_container_end()
            
        elif field_begin["id"] == 12:
            local_container = reader.read_container_begin()
            if local_container["elementType"] != BondDataType.BT_LIST:
                Logger.log_error(
                    f"Error deserializing value, wrong container type for doubleArray, expected list found {local_container['elementType']}"
                )
                return {"status": False, "value": local_value}
                
            for _ in range(local_container["size"]):
                internal_double_container = reader.read_container_begin()
                if internal_double_container["elementType"] != BondDataType.BT_DOUBLE:
                    Logger.log_error(
                        f"Error deserializing value, wrong container type for doubleArray element, expected double found {internal_double_container['elementType']}"
                    )
                    return {"status": False, "value": local_value}
                    
                local_double = []
                for _ in range(internal_double_container["size"]):
                    local_double.append(reader.read_double())
                    
                local_value.double_array.append(local_double)
                reader.read_container_end()
                
            reader.read_container_end()
            
        elif field_begin["id"] == 13:
            local_container = reader.read_container_begin()
            if local_container["elementType"] != BondDataType.BT_LIST:
                Logger.log_error(
                    f"Error deserializing value, wrong container type for guidArray, expected list found {local_container['elementType']}"
                )
                return {"status": False, "value": local_value}
                
            for _ in range(local_container["size"]):
                internal_guid_array_container = reader.read_container_begin()
                if internal_guid_array_container["elementType"] != BondDataType.BT_LIST:
                    Logger.log_error(
                        f"Error deserializing value, wrong container type for guidArray element, expected list found {internal_guid_array_container['elementType']}"
                    )
                    return {"status": False, "value": local_value}
                    
                local_guid_array = []
                for _ in range(internal_guid_array_container["size"]):
                    internal_guid_container = reader.read_container_begin()
                    if internal_guid_container["elementType"] != BondDataType.BT_UINT8:
                        Logger.log_error(
                            f"Error deserializing value, wrong container type for guidArray element internal, expected uint8 found {internal_guid_container['elementType']}"
                        )
                        return {"status": False, "value": local_value}
                        
                    local_guids = []
                    for _ in range(internal_guid_container["size"]):
                        local_guids.append(reader.read_uint8())
                        
                    local_guid_array.append(local_guids)
                    reader.read_container_end()
                    
                local_value.guid_array.append(local_guid_array)
                reader.read_container_end()
                
            reader.read_container_end()
            
        else:
            Logger.log_error(f"Error deserializing value, unknown type {field_begin['id']}")
            return {"status": False, "value": local_value}
        
        reader.read_field_end()

    return {"status": True, "value": local_value}
