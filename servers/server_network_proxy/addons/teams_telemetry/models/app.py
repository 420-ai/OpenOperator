class App:
    def __init__(self):
        # 1: optional string expId
        self.exp_id: str = ""
        # 2: optional string userId
        self.user_id: str = ""
        # 3: optional string env
        self.env: str = ""
        # 4: optional int32 asId
        self.as_id: int = 0
        # 5: optional string id
        self.id: str = ""
        # 6: optional string ver
        self.ver: str = ""
        # 7: optional string locale
        self.locale: str = ""
        # 8: optional string name
        self.name: str = ""

    def to_json(self):
        return {
            "expId": self.exp_id,
            "userId": self.user_id,
            "env": self.env,
            "asId": self.as_id,
            "id": self.id,
            "ver": self.ver,
            "locale": self.locale,
            "name": self.name
        }
