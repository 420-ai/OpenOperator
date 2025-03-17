class Sdk:
    def __init__(self):
        # 1: optional string libVer
        self.lib_ver: str = ""
        # 2: optional string epoch
        self.epoch: str = ""
        # 3: optional int64 seq
        self.seq: int = 0
        # 4: optional string installId
        self.install_id: str = ""

    def to_json(self):
        return {
            "libVer": self.lib_ver,
            "epoch": self.epoch,
            "seq": self.seq,
            "installId": self.install_id
        }
