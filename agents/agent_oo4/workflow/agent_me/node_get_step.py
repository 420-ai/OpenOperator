from state import State
from tracker import Tracker
from clients.llm import llm_phi4, calculate_cost
from autogen_core.models import UserMessage, SystemMessage
from helpers import format_autogen_message

import logging
logger = logging.getLogger("agent_me--node_get_step")

SYSTEM_MESSAGE = """
You are a helpful assistant that helps the user to get the first step of the plan. Do not elaborate on the plan, just return the first step.
"""

USER_MESSAGE = """
Here is the plan, return only the first step of the plan:
{plan}
"""

class NodeGetStep:
    """
    Get the first step from the plan.
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_get_step"
        self.description = "Get the first step from the plan."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_phi4

    async def execute(self) -> None:
        logger.debug("Executing...")

        # Get the plan from state
        plan = self.state.current_plan_data["plan_text"]

        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        user_message = UserMessage(content=[
            USER_MESSAGE.format(plan=plan),
        ], source="user")

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message)
        ])
        # endregion

        # LLM call
        result = await self.llm.create(
            messages=[
                system_message,
                user_message
            ]
        )

        # ---- COST CALCULATION ----
        model_name, total_cost = calculate_cost(result.usage, self.llm._resolved_model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Model: {model_name}, Total cost: {total_cost}$")
        logger.debug(format_autogen_message(result))

        self.state.save_plan_step_text(result.content)

        self.tracker.save(self.name, [
            ("llm_response", result),
            ("cost", f"{total_cost}$"),
        ])
        # endregion
        