class Net:
    def __init__(self):
        # 1: optional string provider
        self.provider: str = ""
        # 2: optional string cost
        self.cost: str = ""
        # 3: optional string type
        self.type: str = ""

    def to_json(self):
        return {
            "provider": self.provider,
            "cost": self.cost,
            "type": self.type
        }
