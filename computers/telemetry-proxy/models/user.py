class User:
    def __init__(self):
        # 1: optional string id
        self.id: str = ""
        # 2: optional string localId
        self.local_id: str = ""
        # 3: optional string authId
        self.auth_id: str = ""
        # 4: optional string locale
        self.locale: str = ""

    def to_json(self):
        return {
            "id": self.id,
            "localId": self.local_id,
            "authId": self.auth_id,
            "locale": self.locale
        }
