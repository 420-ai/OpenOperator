import sys
import re
from core.state import State
from core.tracker import Tracker

import logging
logger = logging.getLogger("node_get_step")

def extract_execution_plan(text: str) -> list[str]:
    # Use regex to find the content of the "Execution Plan" section
    match = re.search(r"### Execution Plan:\s*(.*?)(?=\n###|\Z)", text, re.DOTALL)
    if not match:
        return []

    execution_section = match.group(1).strip()

    # Find all numbered list items (e.g., "1. Some text")
    steps = re.findall(r"\d+\.\s+(.*?)(?=\n\d+\.|\Z)", execution_section, re.DOTALL)

    # Clean up the steps (remove any unnecessary whitespace)
    return [step.strip().replace('\n', ' ') for step in steps]

class NodeGetStep:
    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "node_get_step"
        self.description = "Node responsible for parsing the plan and getting the first step"

        self.config = state.get_config()
        self.state = state
        self.tracker = tracker

    async def execute(self) -> str:

        # Get the plan from state
        plan = self.state.current_plan_data["plan_text"]

        # Extract the execution plan
        steps = extract_execution_plan(plan)

        first_step = steps[0]

        if not first_step:
            logger.error("No steps found in the execution plan.")
            raise ValueError("No steps found in the execution plan.")

        # Save the step in the state
        self.state.save_plan_step_text(first_step)
