import subprocess
import importlib
from typing import List, Tuple
from models import EvaluationRequest, EvaluationResponse


def execute_command(command: str, shell: bool = True) -> str:
    result = subprocess.run(command, shell=shell, capture_output=True, text=True)
    return result.stdout + result.stderr


def validate_output(
    output: str, include_rules: List[str], exclude_rules: List[str]
) -> Tuple[bool, str]:
    for rule in include_rules:
        if rule not in output:
            return False, f"Missing required output: '{rule}'"
    for rule in exclude_rules:
        if rule in output:
            return False, f"Found excluded output: '{rule}'"
    return True, "Output validation passed."


def process_evaluation(request: EvaluationRequest) -> EvaluationResponse:
    success = True
    message = ""

    for evaluator_item in request.evaluation:
        evaluator_name = evaluator_item.evaluator

        try:
            # Dynamically load the evaluator module
            module_path = f"evaluators.{evaluator_name}"

            evaluator_module = importlib.import_module(module_path)

            # Get the evaluator class (assuming naming convention: EvaluatorXxxYyy)
            class_name = f"Evaluator{''.join(word.capitalize() for word in evaluator_name.split('_'))}"
            evaluator_class = getattr(evaluator_module, class_name)

            # Instantiate the evaluator
            evaluator_instance = evaluator_class()

            # Call the evaluate method
            result = evaluator_instance.evaluate(evaluator_item)

            if isinstance(result, tuple) and len(result) >= 2:
                success = success and result[0]
                message = message + result[1] + "\n"
            elif isinstance(result, bool):
                success = success and result[0]
                message = (
                    message + f"Evaluation {evaluator_name} completed\n"
                    if result
                    else f"Evaluation {evaluator_name} failed\n"
                )
            else:
                success = False
                message = "Invalid evaluator result format"

        except Exception as e:
            return EvaluationResponse(
                success=False,
                message=f"Error loading or executing evaluator '{evaluator_name}': {str(e)}",
            )

    return EvaluationResponse(success=success, message=message)
