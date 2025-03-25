from typing import Dict, Any, List

import requests
import logging
import os

def get_evaluation_results(evaluators: List[Dict[str, Any]]):
    logging.info("Getting evaluation results from evaluator")
    
    evaulator_url = os.getenv("EVALUATOR_URL")

    response = requests.get(f"{evaulator_url}/evaluate", json=evaluators)
    
    if response.status_code == 200:
        try:
            response_json = response.json()
            logging.info("Got evaluation results from evaluator")
            return response_json
        except ValueError:
            logging.error("Failed to parse JSON response from evaluator")
            return None
    else:
        logging.error(f"Failed to get evaluation results from evaluator: {response.status_code} - {response.text}")
