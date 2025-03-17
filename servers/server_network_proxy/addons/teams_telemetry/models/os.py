class Os:
    def __init__(self):
        # 1: optional string locale
        self.locale: str = ""
        # 2: optional string expId
        self.exp_id: str = ""
        # 3: optional int32 bootId
        self.boot_id: int = 0
        # 4: optional string name
        self.name: str = ""
        # 5: optional string ver
        self.ver: str = ""

    def to_json(self):
        return {
            "locale": self.locale,
            "expId": self.exp_id,
            "bootId": self.boot_id,
            "name": self.name,
            "ver": self.ver
        }
