from ...bond.bond_const import BondDataType
from ...bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from ...models.attribute import Attribute
from .deserialize_pii import deserialize_pii
from .deserialize_customer_content import deserialize_customer_content


def deserialize_attribute(reader: IProtocolReader) -> dict:
    """
    Deserialize an Attribute object from the protocol reader.
    Returns a tuple containing the status (bool) and the deserialized attribute object.
    """
    local_attribute = Attribute()
    reader.read_struct_begin()

    while True:
        field_begin = reader.read_field_begin_unknown()
        if field_begin["result"] == False:
            Logger.log_error("Error deserializing attribute, can't find field begin")
            return {"status": False, "attribute": local_attribute}

        if (
            field_begin["type"] == BondDataType.BT_STOP
            or field_begin["type"] == BondDataType.BT_STOP_BASE
        ):
            break

        if field_begin["id"] == 1:
            local_container = reader.read_container_begin()
            if local_container["element_type"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing attribute, wrong container type for pii, expected struct found {local_container['element_type']}"
                )
                return {"status": False, "attribute": local_attribute}

            for _ in range(local_container["size"]):
                pii = deserialize_pii(reader)
                if not pii["status"]:
                    Logger.log_error(
                        "Error deserializing attribute, error deserializing pii"
                    )
                    return {"status": False, "attribute": local_attribute}

                local_attribute.pii.append(pii["pii"])

            reader.read_container_end()
        elif field_begin["id"] == 2:
            local_container = reader.read_container_begin()
            if local_container["element_type"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing attribute, wrong container type for customer content, expected struct found {local_container['element_type']}"
                )
                return {"status": False, "attribute": local_attribute}

            for _ in range(local_container["size"]):
                cc = deserialize_customer_content(reader)
                if not cc["status"]:
                    Logger.log_error(
                        "Error deserializing attribute, error deserializing customer content"
                    )
                    return {"status": False, "attribute": local_attribute}

                local_attribute.customer_content.append(cc["cc"])

            reader.read_container_end()
        else:
            Logger.log_error(
                f"Error deserializing attribute, unknown type {field_begin['id']}"
            )
            return {"status": False, "attribute": local_attribute}

        reader.read_field_end()

    return {"status": True, "attribute": local_attribute}
