from typing import Tuple
from bond.bond_const import BondDataType
from bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from models.device import Device


def deserialize_device(reader: IProtocolReader) -> dict:
    """
    Deserialize a Device object from the protocol reader.
    Returns a tuple containing the status (bool) and the deserialized device object.
    """
    local_device = Device()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log_error("Error deserializing Device, can't find field begin")
            return {"status": False, "device": local_device}

        if (
            field_begin["type"] == BondDataType.BT_STOP
            or field_begin["type"] == BondDataType.BT_STOP_BASE
        ):
            break

        if field_begin["id"] == 1:
            local_device.id = reader.read_string()
        elif field_begin["id"] == 2:
            local_device.local_id = reader.read_string()
        elif field_begin["id"] == 3:
            local_device.auth_id = reader.read_string()
        elif field_begin["id"] == 4:
            local_device.auth_sec_id = reader.read_string()
        elif field_begin["id"] == 5:
            local_device.device_class = reader.read_string()
        elif field_begin["id"] == 6:
            local_device.org_id = reader.read_string()
        elif field_begin["id"] == 7:
            local_device.org_auth_id = reader.read_string()
        elif field_begin["id"] == 8:
            local_device.make = reader.read_string()
        elif field_begin["id"] == 9:
            local_device.model = reader.read_string()
        else:
            Logger.log_error(
                f"Error deserializing device, unknown type {field_begin['id']}"
            )
            return {"status": False, "device": local_device}

        reader.read_field_end()

    return {"status": True, "device": local_device}
