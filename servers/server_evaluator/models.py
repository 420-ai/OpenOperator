from pydantic import BaseModel
from typing import Dict, Any


class EvaluationRequest(BaseModel):
    name: str  # Function name to call
    args: Dict[str, Any] = {}  # Flexible arguments
