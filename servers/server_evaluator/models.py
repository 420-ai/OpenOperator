from pydantic import BaseModel
from typing import List, Dict


class EvaluationRequest(BaseModel):
    telemetry_file: str
    markers: List[Dict[str, str]]  # flexible key-value dict per marker
