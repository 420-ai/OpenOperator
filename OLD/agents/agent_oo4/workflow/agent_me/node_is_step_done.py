from typing import Tuple
from state import State
from tracker import Tracker
from clients.llm import llm_gpt4o_mini, llm_llama32_vision, calculate_cost
from helpers import encode_image, fm

import logging
logger = logging.getLogger("agent_me--node_is_step_done")

SYSTEM_MESSAGE = """
You are an AI agent responsible for deciding whether the specified step has already been successfully completed, based on a screenshot of the GUI.

Your task is to:
- Determine if the user has already **completed** the step.
- Do not assume the step is done just because the UI element is visible.
- Only mark the step as done if there is clear **evidence** that the action (e.g. click, selection, navigation) was performed.
- Be conservative. If there is uncertainty, assume the step is NOT completed.

Output format:
RESULT: <TRUE or FALSE>
REASON: <a short explanation of why you made this decision, based only on visible evidence>
"""

USER_MESSAGE = """
Here is the step the agent should complete:
===========================
{plan_step}
===========================

Attached is the current screenshot of the GUI after attempting the step. Based on the visual state of the interface, determine if the step has already been successfully completed.
"""

class NodeIsStepDone:
    """
    Check if the step is done.
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_is_step_done"
        self.description = "Check if the step is done."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        # self.llm = llm_gpt4o_mini
        self.llm = llm_llama32_vision

    async def execute(self) -> Tuple[bool, str]:
        logger.debug("Executing...")
        
        # Get the plan step from state
        plan_step = self.state.current_plan_data["plan_step"]["text"]
        # Get the screenshot from state
        screenshot_t0 = self.state.get_current_plan_image("t0")
        
        system_message = {"role": "system", "content": SYSTEM_MESSAGE }
        user_message = {
            "role": "user", 
            "content":  [
                {
                    "type": "text",
                    "text":  USER_MESSAGE.format(plan_step=plan_step)
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encode_image(screenshot_t0)}",
                    }
                }
            ]
        }

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message),
            ("screenshot_t0", screenshot_t0)
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

        result_boolean = detect_boolean_value(result.message)

        return result_boolean, result.message
    
def _str_to_bool(value: str) -> bool:
    value = value.strip().lower()
    if value == "true":
        return True
    elif value == "false":
        return False
    else:
        raise ValueError(f"Invalid boolean string: '{value}'. Expected 'TRUE' or 'FALSE'.")

def detect_boolean_value(text):
    text_upper = text.upper()
    
    if "FALSE" in text_upper:
        return False
    elif "TRUE" in text_upper:
        return True
    else:
        return None