import subprocess
from typing import List, Tuple
from models import EvaluationRequest, EvaluationResponse

def execute_command(command: str, shell: bool = True) -> str:
    result = subprocess.run(command, shell=shell, capture_output=True, text=True)
    return result.stdout + result.stderr

def validate_output(output: str, include_rules: List[str], exclude_rules: List[str]) -> Tuple[bool, str]:
    for rule in include_rules:
        if rule not in output:
            return False, f"Missing required output: '{rule}'"
    for rule in exclude_rules:
        if rule in output:
            return False, f"Found excluded output: '{rule}'"
    return True, "Output validation passed."

def process_evaluation(request: EvaluationRequest) -> EvaluationResponse:
    command = request.evaluation.result.command
    shell = request.evaluation.result.shell
    output = execute_command(command, shell)
    include_rules = request.evaluation.expected.rules.include
    exclude_rules = request.evaluation.expected.rules.exclude
    success, message = validate_output(output, include_rules, exclude_rules)
    return EvaluationResponse(success=success, message=message, output=output)
