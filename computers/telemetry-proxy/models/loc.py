class Loc:
    def __init__(self):
        # 1: optional string id
        self.id: str = ""
        # 2: optional string country
        self.country: str = ""
        # 3: optional string timezone
        self.timezone: str = ""

    def to_json(self):
        return {
            "id": self.id,
            "country": self.country,
            "timezone": self.timezone
        }
