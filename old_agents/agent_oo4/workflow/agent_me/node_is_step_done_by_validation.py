from state import State
from tracker import Tracker
from clients.llm import llm_gpt4o_mini, calculate_cost
from helpers import fm

import logging
logger = logging.getLogger("agent_me--node_is_step_done_by_validation")

SYSTEM_MESSAGE = """
You are AI agent responsible for deciding, if the step is already done, based on the provided validation.

Output:
Return "TRUE" if the step is already done or can be skipped.
Return "FALSE" if the step we can proceed with the step
"""

USER_MESSAGE = """
Here is the validation summary.

{validation}
"""

class NodeIsStepDoneByValidation:
    """
    Check if the step is done.
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_is_step_done_by_validation"
        self.description = "Check if the step is done by validation."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_gpt4o_mini

    async def execute(self, validation: str) -> bool:
        logger.debug("Executing...")

        # Define new messages
        system_message = {"role": "system", "content": SYSTEM_MESSAGE }
        user_message = {
            "role": "user", 
            "content":  [
                {
                    "type": "text",
                    "text":  USER_MESSAGE.format(validation=validation)
                }
            ]
        }

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message)
        ])
        # endregion
        
        result = self.llm.call(
            messages=[
                system_message,
                user_message
            ]
        )

        # ---- COST CALCULATION ----
        total_cost = calculate_cost(result.usage, self.llm.model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Model: {self.llm.model}, Total cost: {total_cost}$")
        logger.debug(fm(result.message))

        self.tracker.save(self.name, [
            ("llm_response", result.message),
            ("cost", f"{total_cost}$"),
        ])
        # endregion
        
        return _str_to_bool(result.message)
    

def _str_to_bool(value: str) -> bool:
    value = value.strip().lower()
    if value == "true":
        return True
    elif value == "false":
        return False
    else:
        raise ValueError(f"Invalid boolean string: '{value}'. Expected 'TRUE' or 'FALSE'.")
