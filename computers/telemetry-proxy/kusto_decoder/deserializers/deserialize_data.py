from typing import Tuple
from bond.bond_const import BondDataType
from bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from models.data import Data
from .deserialize_value import deserialize_value


def deserialize_data(reader: IProtocolReader) -> dict:
    """
    Deserialize a Data object from the protocol reader.
    Returns a tuple containing the status (bool) and the deserialized data object.
    """
    local_data = Data()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()

        if field_begin["result"] == False:
            Logger.log_error("Error deserializing data, can't find field begin")
            return {"status": False, "data": local_data}

        if (
            field_begin["type"] == BondDataType.BT_STOP
            or field_begin["type"] == BondDataType.BT_STOP_BASE
        ):
            break

        if field_begin["id"] == 1:
            map_container_data = reader.read_map_container_begin()
                      
            if (
                map_container_data["keyType"] != BondDataType.BT_STRING
                or map_container_data["valueType"] != BondDataType.BT_STRUCT
            ):
                return {"status": False, "data": local_data}

            for _ in range(map_container_data["size"]):
                key = reader.read_string()
                if not key:
                    Logger.log_error("Error deserializing data, can't find key value")
                    return {"status": False, "data": local_data}

                value = deserialize_value(reader)
                if not value["status"]:
                    Logger.log_error("Error deserializing data, can't find value")
                    return {"status": False, "data": local_data}

                local_data.properties_.append({"key": key, "value": value["value"]})
        else:
            Logger.log_error(f"Error deserializing data, wrong id {field_begin['id']}")
            return {"status": False, "data": local_data}

        reader.read_field_end()

    return {"status": True, "data": local_data}
