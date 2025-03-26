from typing import Any

import requests
import logging
import os
import json

from core.state import State


def get_evaluation_results(evaluation: Any, state: State):
    logging.info(f"evaluation: {evaluation}")

    logging.info("Getting evaluation results from evaluator")

    evaulator_url = os.getenv("EVALUATOR_URL", "http://localhost:5053")

    response = requests.post(f"{evaulator_url}/evaluate", json={"evaluation": evaluation})

    if response.status_code == 200:
        try:
            response_json = response.json()
            logging.info(f"Got evaluation results from evaluator: {response_json}")

            state.save_evaluation_result(
                json.dumps(response_json, indent=2, sort_keys=True)
            )

            return response_json
        except ValueError:
            logging.error("Failed to parse JSON response from evaluator")
            return None
    else:
        logging.error(
            f"Failed to get evaluation results from evaluator: {response.status_code} - {response.text}"
        )


if __name__ == "__main__":
    # Example usage

    ## setup logging
    logging.basicConfig(level=logging.INFO)

    evaluation = [
        {
            "evaluator": "teams_scenarios",
            "scenarios": ["chat_switch"],
            "telemetry_file": r"/data/logs/teams-telemetry/teams-telemetry-0.log"
        }
    ]
    

    class MockState:
        def save_evaluation_result(self, y): 
            print(f"Saved evaluation result: {y}")

    state = MockState()
    
    result = get_evaluation_results(evaluation, state)
    print(result)
