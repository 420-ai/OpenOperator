import json 
from datetime import datetime
from typing import Literal, Union, List, Optional, Dict, Any
from core.models import Message

def parse_timestamp(ts: Union[int, str]) -> datetime:
    if isinstance(ts, int):
        return datetime.fromtimestamp(ts)
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
