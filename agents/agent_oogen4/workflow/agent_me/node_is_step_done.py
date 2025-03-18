from config import OOConfig
from state import State
from tracker import Tracker
from clients.llm import llm_gpt4o_mini, calculate_cost
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage
from helpers import format_autogen_message

import logging
logger = logging.getLogger("agent_me--node_is_step_done")

SYSTEM_MESSAGE = """
You are AI agent responsible for deciding, if the step is already done, based on the screenshot.

Output:
Return "TRUE" if the step is already done or can be skipped.
Return "FALSE" if the step we can proceed with the step
"""

USER_MESSAGE = """
Here is the step that agent should do, is the step already done?

{plan_step}

Attached is current state of the UI.
"""

class NodeIsStepDone:
    """
    Check if the step is done.
    """

    def __init__(self, config: OOConfig, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_is_step_done"
        self.description = "Check if the step is done."

        self.state = state
        self.config = config
        self.tracker = tracker

        self.llm = llm_gpt4o_mini

    async def execute(self) -> bool:
        logger.debug("Executing...")
        
        # Get the plan step from state
        plan_step = self.state.current_plan_data["plan_step"]["text"]
        # Get the screenshot from state
        screenshot_t0 = self.state.get_current_plan_image("t0")

        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        user_message = UserMessage(content=[
            USER_MESSAGE.format(plan_step=plan_step),
            AutogenImage.from_pil(screenshot_t0) 
        ], source="user")

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message)
        ])
        # endregion

        result = await self.llm.create(
            messages=[
                system_message,
                user_message
            ]
        )

        # ---- COST CALCULATION ----
        total_cost = calculate_cost(result.usage, self.llm._resolved_model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Total cost: {total_cost}$")
        logger.debug(format_autogen_message(result))

        self.tracker.save(self.name, [
            ("llm_response", result),
            ("cost", f"{total_cost}$"),
        ])
        # endregion

        return _str_to_bool(result.content)
    

def _str_to_bool(value: str) -> bool:
    value = value.strip().lower()
    if value == "true":
        return True
    elif value == "false":
        return False
    else:
        raise ValueError(f"Invalid boolean string: '{value}'. Expected 'TRUE' or 'FALSE'.")
