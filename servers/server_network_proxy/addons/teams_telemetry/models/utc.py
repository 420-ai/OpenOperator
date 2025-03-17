class Utc:
    def __init__(self):
        # 1: optional string stId
        self.st_id: str = ""
        # 2: optional string aId
        self.a_id: str = ""
        # 3: optional string raId
        self.ra_id: str = ""
        # 4: optional string op
        self.op: str = ""
        # 5: optional int64 cat
        self.cat: int = 0
        # 6: optional int64 flags
        self.flags: int = 0
        # 7: optional string sqmId
        self.sqm_id: str = ""
        # 9: optional string mon
        self.mon: str = ""
        # 10: optional int32 cpId
        self.cp_id: int = 0
        # 11: optional string bSeq
        self.b_seq: str = ""
        # 12: optional string epoch
        self.epoch: str = ""
        # 13: optional int64 seq
        self.seq: int = 0
        # 14: optional double popSample
        self.pop_sample: float = 0.0
        # 15: optional int64 eventFlags
        self.event_flags: int = 0

    def to_json(self):
        return {
            "stId": self.st_id,
            "aId": self.a_id,
            "raId": self.ra_id,
            "op": self.op,
            "cat": self.cat,
            "flags": self.flags,
            "sqmId": self.sqm_id,
            "mon": self.mon,
            "cpId": self.cp_id,
            "bSeq": self.b_seq,
            "epoch": self.epoch,
            "seq": self.seq,
            "popSample": self.pop_sample,
            "eventFlags": self.event_flags
        }
