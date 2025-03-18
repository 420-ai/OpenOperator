from pydantic import BaseModel
from typing import List, Literal

   
class TeamsScenariosArgs(BaseModel):
    evaluator: Literal["teams_scenarios"]
    scenarios: List[str]
    telemetry_file: str

class EvaluationRequest(BaseModel):
    evaluation: List[TeamsScenariosArgs]
    
class EvaluationResponse(BaseModel):
    success: bool
    message: str
