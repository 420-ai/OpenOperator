from typing import Tuple
from ...bond.microsoft_bond import BondDataType, IProtocolReader
from ..utils.logger import Logger
from ...models.loc import Loc


def deserialize_loc(reader: IProtocolReader) -> dict:
    """
    Deserialize a Loc object from the protocol reader.
    Returns a tuple containing the status (bool) and the deserialized loc object.
    """
    local_loc = Loc()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log_error("Error deserializing loc, can't find field begin")
            return {"status": False, "loc": local_loc}

        if (
            field_begin["type"] == BondDataType.BT_STOP
            or field_begin["type"] == BondDataType.BT_STOP_BASE
        ):
            break

        if field_begin["id"] == 1:
            local_loc.id = reader.read_string()
        elif field_begin["id"] == 2:
            local_loc.country = reader.read_string()
        elif field_begin["id"] == 3:
            local_loc.timezone = reader.read_string()
        else:
            Logger.log_error(
                f"Error deserializing Loc, unknown type {field_begin['id']}"
            )
            return {"status": False, "loc": local_loc}

        reader.read_field_end()

    return {"status": True, "loc": local_loc}
