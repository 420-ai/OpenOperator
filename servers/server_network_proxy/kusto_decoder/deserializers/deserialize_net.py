from typing import Tuple
from bond.microsoft_bond import BondDataType, IProtocolReader
from ..utils.logger import Logger
from models.net import Net


def deserialize_net(reader: IProtocolReader) -> dict:
    """
    Deserialize a Net object from the protocol reader.
    Returns a tuple containing the status (bool) and the deserialized net object.
    """
    local_net = Net()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log_error("Error deserializing net, can't find field begin")
            return {"status": False, "net": local_net}

        if (
            field_begin["type"] == BondDataType.BT_STOP
            or field_begin["type"] == BondDataType.BT_STOP_BASE
        ):
            break

        if field_begin["id"] == 1:
            local_net.provider = reader.read_string()
        elif field_begin["id"] == 2:
            local_net.cost = reader.read_string()
        elif field_begin["id"] == 3:
            local_net.type = reader.read_string()
        else:
            Logger.log_error(
                f"Error deserializing net, unknown type {field_begin['id']}"
            )
            return {"status": False, "net": local_net}

        reader.read_field_end()

    return {"status": True, "net": local_net}
