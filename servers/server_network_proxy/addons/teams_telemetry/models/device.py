class Device:
    def __init__(self):
        # 1: optional string id
        self.id: str = ""
        # 2: optional string localId
        self.local_id: str = ""
        # 3: optional string authId
        self.auth_id: str = ""
        # 4: optional string authSecId
        self.auth_sec_id: str = ""
        # 5: optional string deviceClass
        self.device_class: str = ""
        # 6: optional string orgId
        self.org_id: str = ""
        # 7: optional string orgAuthId
        self.org_auth_id: str = ""
        # 8: optional string make
        self.make: str = ""
        # 9: optional string model
        self.model: str = ""

    def to_json(self):
        return {
            "id": self.id,
            "localId": self.local_id,
            "authId": self.auth_id,
            "authSecId": self.auth_sec_id,
            "deviceClass": self.device_class,
            "orgId": self.org_id,
            "orgAuthId": self.org_auth_id,
            "make": self.make,
            "model": self.model
        }
