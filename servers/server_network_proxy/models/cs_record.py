from typing import Dict, List, Any
from .app import App
from .data import Data
from .device import Device
from .loc import Loc
from .m365a import M365a
from .net import Net
from .os import Os
from .protocol import Protocol
from .sdk import Sdk
from .user import User
from .utc import Utc

class CsRecord:
    def __init__(self):
        # 1: optional string Id
        self.version: str = ""
        # 2: string name
        self.name: str = ""
        # 3: optional int64 Timestamp
        self.timestamp: int = 0
        # 4: optional double popSample
        self.pop_sample: float = 100.0
        # 5: optional string Type
        self.type: str = ""
        # 6: optional string EventType
        self.event_type: int = 0
        # 7: optional stringg cV
        self.c_v: str = ""
        # 21: optional extProtocol
        self.ext_protocol: List[Protocol] = []
        # 22: optional extUser
        self.ext_user: List[User] = []
        # 23: optional extDevice
        self.ext_device: List[Device] = []
        # 24: optional extOs
        self.ext_os: List[Os] = []
        # 25: optional extApp
        self.ext_app: List[App] = []
        # 26: optional extUtc
        self.ext_utc: List[Utc] = []
        # 31: optional extNet
        self.ext_net: List[Net] = []
        # 32: optional extSdk
        self.ext_sdk: List[Sdk] = []
        # 33: optional extLock
        self.ext_lock: List[Loc] = []
        # 37: optional extM365a
        self.ext_m365a: List[M365a] = []
        # 41: optional ext
        self.ext: List[Data] = []
        # 51: optional tags
        self.tags: Dict[str, str] = {}
        # 60: base type
        self.base_type: str = ""
        # 61: BaseData
        self.base_data: List[Data] = []
        # 70: Optional data
        self.data: List[Data] = []

    def to_json(self):
        protocol_array = []
        user_array = []
        device_array = []
        os_array = []
        app_array = []
        utc_array = []
        net_array = []
        sdk_array = []
        loc_array = []
        m365_array = []
        ext_data = {}
        base_data = {}
        data = {}
        
        for single_protocol in self.ext_protocol:
            protocol_array.append(single_protocol.to_json())
        for single_user in self.ext_user:
            user_array.append(single_user.to_json())
        for single_device in self.ext_device:
            device_array.append(single_device.to_json())
        for single_os in self.ext_os:
            os_array.append(single_os.to_json())
        for single_app in self.ext_app:
            app_array.append(single_app.to_json())
        for single_utc in self.ext_utc:
            utc_array.append(single_utc.to_json())
        for single_net in self.ext_net:
            net_array.append(single_net.to_json())
        for single_sdk in self.ext_sdk:
            sdk_array.append(single_sdk.to_json())
        for single_loc in self.ext_lock:
            loc_array.append(single_loc.to_json())
        for single_m365 in self.ext_m365a:
            m365_array.append(single_m365.to_json())
            
        for single_data in self.ext:
            ext_data.update(single_data.to_json())
        for single_data in self.base_data:
            base_data.update(single_data.to_json())
        for single_data in self.data:
            data.update(single_data.to_json())
            
        return {
            "version": self.version,
            "name": self.name,
            "timestamp": self.timestamp,
            "popSample": self.pop_sample,
            "type": self.type,
            "eventType": self.event_type,
            "cV": self.c_v,
            "extProtocol": protocol_array,
            "extUser": user_array,
            "extDevice": device_array,
            "extOs": os_array,
            "extApp": app_array,
            "extUTC": utc_array,
            "extNet": net_array,
            "extSdk": sdk_array,
            "extLock": loc_array,
            "extM365a": m365_array,
            "ext": ext_data,
            "tags": self.tags,
            "baseType": self.base_type,
            "baseData": base_data,
            "data": data
        }
