from typing import List

class Protocol:
    def __init__(self):
        # 1: optional int32 metadataCrc
        self.metadata_crc: int = 0
        # 2: optional vector of strings, ticketkey
        self.ticket_keys: List[List[str]] = []
        # 3: optional string devMake
        self.dev_make: str = ""
        # 4: optional string devModel
        self.dev_model: str = ""

    def to_json(self):
        return {
            "metadataCrc": self.metadata_crc,
            "ticketKeys": self.ticket_keys,
            "devMake": self.dev_make,
            "devModel": self.dev_model
        }
