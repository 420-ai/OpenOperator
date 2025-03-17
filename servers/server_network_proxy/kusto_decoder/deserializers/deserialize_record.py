from bond.bond_const import BondDataType
from bond.microsoft_bond import IProtocolReader
from ..utils.logger import Logger
from models.cs_record import CsRecord
from .deserialize_protocol import deserialize_protocol
from .deserialize_user import deserialize_user
from .deserialize_device import deserialize_device
from .deserialize_os import deserialize_os
from .deserialize_app import deserialize_app
from .deserialize_utc import deserialize_utc
from .deserialize_net import deserialize_net
from .deserialize_sdk import deserialize_sdk
from .deserialize_loc import deserialize_loc
from .deserialize_m365a import deserialize_m365a
from .deserialize_data import deserialize_data


def deserialize_record(reader: IProtocolReader) -> dict:
    """
    Deserialize a CsRecord object from the protocol reader

    Returns:
        dict: Contains 'status' (bool) and 'record' (CsRecord)
    """

    output_record = CsRecord()
    reader.read_struct_begin()

    while True:
        response = None
        try:
            response = reader.read_field_begin_unknown()
        except Exception:
            pass
        
        if not response["result"]:
            Logger.log("Error detecting field begin on Record")
            return {"status": False, "record": output_record}

        if (
            response["type"] == BondDataType.BT_STOP
            or response["type"] == BondDataType.BT_STOP_BASE
        ):
            # we don't use base
            break

        if response["id"] == 1:
            # read string version
            output_record.version = reader.read_string()

        elif response["id"] == 2:
            # read string name
            output_record.name = reader.read_string()

        elif response["id"] == 3:
            # read int64 time
            output_record.timestamp = reader.read_int64_to_number()

        elif response["id"] == 4:
            # Read double pop sample
            output_record.pop_sample = reader.read_double()

        elif response["id"] == 5:
            # read string iKey
            output_record.type = reader.read_string()

        elif response["id"] == 6:
            # read int64 flags
            output_record.event_type = reader.read_int64_to_number()

        elif response["id"] == 7:
            # read string cV
            output_record.cV = reader.read_string()

        elif response["id"] == 21:
            # container, a bit more complex, extProtocol
            container_data = reader.read_container_begin()
            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extProtocol, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                protocol = deserialize_protocol(reader)
                if not protocol["status"]:
                    Logger.log_error("Error deserializing extProtocol")
                    return {"status": False, "record": output_record}
                output_record.ext_protocol.append(protocol["protocol"])

            reader.read_container_end()

        elif response["id"] == 22:
            # Container, extUser
            container_data = reader.read_container_begin()

            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extUser, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_user = deserialize_user(reader)
                if not local_user["status"]:
                    Logger.log_error("Error deserializing extUser")
                    return {"status": False, "record": output_record}
                output_record.ext_user.append(local_user["user"])

            reader.read_container_end()

        elif response["id"] == 23:
            # Container extDevice
            container_data = reader.read_container_begin()
            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extDevice, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_device = deserialize_device(reader)
                if not local_device["status"]:
                    Logger.log_error("Error deserializing extDevice")
                    return {"status": False, "record": output_record}
                output_record.ext_device.append(local_device["device"])

            reader.read_container_end()

        elif response["id"] == 24:
            # Container extOs
            container_data = reader.read_container_begin()
            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extOs, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_os = deserialize_os(reader)
                if not local_os["status"]:
                    Logger.log_error("Error deserializing extOs")
                    return {"status": False, "record": output_record}
                output_record.ext_os.append(local_os["os"])

            reader.read_container_end()

        elif response["id"] == 25:
            # Container extApp
            container_data = reader.read_container_begin()
            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extApp, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_app = deserialize_app(reader)
                if not local_app["status"]:
                    Logger.log_error("Error deserializing extApp")
                    return {"status": False, "record": output_record}
                output_record.ext_app.append(local_app["app"])

            reader.read_container_end()

        elif response["id"] == 26:
            # Container extUtc
            container_data = reader.read_container_begin()
            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extUtc, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_utc = deserialize_utc(reader)
                if not local_utc["status"]:
                    Logger.log_error("Error deserializing extUtc")
                    return {"status": False, "record": output_record}
                output_record.ext_UTC.append(local_utc["utc"])

            reader.read_container_end()

        elif response["id"] == 31:
            # Container extNet
            container_data = reader.read_container_begin()
            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extNet, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_net = deserialize_net(reader)
                if not local_net["status"]:
                    Logger.log_error("Error deserializing extNet")
                    return {"status": False, "record": output_record}
                output_record.ext_net.append(local_net["net"])

            reader.read_container_end()

        elif response["id"] == 32:
            # Container extSdk
            container_data = reader.read_container_begin()
            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extSdk, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_sdk = deserialize_sdk(reader)
                if not local_sdk["status"]:
                    Logger.log_error("Error deserializing extSdk")
                    return {"status": False, "record": output_record}
                output_record.ext_sdk.append(local_sdk["sdk"])

            reader.read_container_end()

        elif response["id"] == 33:
            # Container extLoc
            container_data = reader.read_container_begin()
            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extLoc, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_loc = deserialize_loc(reader)
                if not local_loc["status"]:
                    Logger.log_error("Error deserializing extLoc")
                    return {"status": False, "record": output_record}
                output_record.ext_lock.append(local_loc["loc"])

            reader.read_container_end()

        elif response["id"] == 37:
            # Container extM365a
            container_data = reader.read_container_begin()
            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing extM365a, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_m365a = deserialize_m365a(reader)
                if not local_m365a["status"]:
                    Logger.log_error("Error deserializing extM365a")
                    return {"status": False, "record": output_record}
                output_record.ext_m365a.append(local_m365a["m365a"])

            reader.read_container_end()

        elif response["id"] == 41:
            # Container ext
            container_data = reader.read_container_begin()

            if container_data["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing ext, element type is not a struct {container_data['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_data["size"]):
                local_ext = deserialize_data(reader)
                if not local_ext["status"]:
                    Logger.log_error("Error deserializing ext")
                    return {"status": False, "record": output_record}
                output_record.ext.append(local_ext["data"])

            reader.read_container_end()

        elif response["id"] == 51:
            # Map of strings tags
            container_begin = reader.read_map_container_begin()
            if (
                container_begin["keyType"] != BondDataType.BT_STRING
                or container_begin["valueType"] != BondDataType.BT_STRING
            ):
                Logger.log_error(
                    f"Error deserializing tags, key or value type are not a string {container_begin['keyType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_begin["size"]):
                local_key = reader.read_string()
                local_value = reader.read_string()
                output_record.tags[local_key] = local_value

            reader.read_container_end()

        elif response["id"] == 60:
            # String base type
            output_record.base_type = reader.read_string()

        elif response["id"] == 61:
            # Container, baseData
            container_begin = reader.read_container_begin()
            if container_begin["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing baseData, element type is not a struct {container_begin['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_begin["size"]):
                local_data = deserialize_data(reader)
                if not local_data["status"]:
                    Logger.log_error("Error deserializing baseData")
                    return {"status": False, "record": output_record}
                output_record.base_data.append(local_data["data"])

            reader.read_container_end()

        elif response["id"] == 70:
            # Container, data
            container_begin = reader.read_container_begin()
            if container_begin["elementType"] != BondDataType.BT_STRUCT:
                Logger.log_error(
                    f"Error deserializing data, element type is not a struct {container_begin['elementType']}"
                )
                return {"status": False, "record": output_record}

            for _ in range(container_begin["size"]):
                local_data = deserialize_data(reader)
                if not local_data["status"]:
                    Logger.log_error("Error deserializing data")
                    return {"status": False, "record": output_record}
                output_record.data.append(local_data["data"])

            reader.read_container_end()

        else:
            Logger.log(f"Unknown id found parsing record {response['id']}")

        reader.read_field_end()

    return {"status": True, "record": output_record}
