from pydantic import BaseModel
from typing import List, Literal

class VMCommandLine(BaseModel):
    type: Literal["vm_command_line"]
    command: str
    shell: bool

class Rules(BaseModel):
    include: List[str] = []
    exclude: List[str] = []

class ExpectedResult(BaseModel):
    type: Literal["rule"]
    rules: Rules

class EvaluationData(BaseModel):
    func: str
    result: VMCommandLine
    expected: ExpectedResult

class EvaluationRequest(BaseModel):
    evaluation: EvaluationData
    
class EvaluationResponse(BaseModel):
    success: bool
    message: str
    output: str
