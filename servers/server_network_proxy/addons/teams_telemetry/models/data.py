from typing import Dict, List
from .value import Value

class Data:
    def __init__(self):
        self.properties_: List[dict] = []

    def to_json(self):
        ret_val = {}
        
        for key_value in self.properties_:
            ret_val[key_value["key"]] = key_value["value"].to_json()
            
        return ret_val
