from typing import Tuple
from ...bond.bond_const import BondDataType
from ...bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from ...models.m365a import M365a


def deserialize_m365a(reader: IProtocolReader) -> dict:
    """
    Deserialize an M365a object from the protocol reader.
    Returns a tuple containing the status (bool) and the deserialized m365a object.
    """
    local_m365a = M365a()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log_error("Error deserializing m365a, can't find field begin")
            return {"status": False, "m365a": local_m365a}

        if (
            field_begin["type"] == BondDataType.BT_STOP
            or field_begin["type"] == BondDataType.BT_STOP_BASE
        ):
            break

        if field_begin["id"] == 1:
            local_m365a.enrolled_tenant_id = reader.read_string()
        else:
            Logger.log_error(
                f"Error deserializing M365a, unknown type {field_begin['id']}"
            )
            return {"status": False, "m365a": local_m365a}

        reader.read_field_end()

    return {"status": True, "m365a": local_m365a}
