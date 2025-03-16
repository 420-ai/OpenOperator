from typing import Tuple
from bond.bond_const import BondDataType
from bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from models.enums import CustomerContentKind


def deserialize_customer_content(reader: IProtocolReader) -> dict:
    """
    Deserialize a CustomerContentKind enum from the protocol reader.
    Returns a tuple containing the status (bool) and the deserialized customer content kind.
    """
    local_cc = CustomerContentKind.NotSet
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log_error(
                "Error deserializing customer content, can't find field begin"
            )
            return {"status": False, "cc": local_cc}

        if (
            field_begin["type"] == BondDataType.BT_STOP
            or field_begin["type"] == BondDataType.BT_STOP_BASE
        ):
            break

        if field_begin["id"] == 1:
            local_cc = CustomerContentKind(reader.read_int32())
        else:
            Logger.log_error(
                f"Error deserializing Customer Content, unknown type {field_begin['id']}"
            )
            return {"status": False, "cc": local_cc}

        reader.read_field_end()

    return {"status": True, "cc": local_cc}
