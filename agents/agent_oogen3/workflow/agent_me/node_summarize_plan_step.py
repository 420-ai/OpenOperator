from typing import Any
from config import OOConfig
from state import State
from tracker import Tracker
from workflow.clients.llm import llm_phi4, calculate_cost
from autogen_core.models import UserMessage, SystemMessage
from helpers import format_autogen_message

import logging
logger = logging.getLogger("agent_me--node_summarize_plan_step")

SYSTEM_MESSAGE = """
You are AI assistant that is helping summarize actions in iterations.
"""

USER_MESSAGE = """
Summarize following actions in all iterations into short text.
==================================
{iterations_history}
==================================
"""

class NodeSummarizePlanStep:
    """
    Summarize actions in iterations
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_summarize_plan_step"
        self.description = "Summarize all history of plan step iterations."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_phi4

    async def execute(self) -> bool:
        logger.debug("Executing...")

        past_iterations = self.state.get_current_plan_step_iterations_data()
        
        if len(past_iterations) > 0:
            # We have some past iterations

            actions_history = ""
            for iteration in past_iterations:
                actions_history += f"Iteration {iteration['iteration_number']}:\n"
                actions_history += f"Actions: {iteration['iteration_actions']}\n"
                actions_history += f"Result: {iteration['validation_result']}\n"

            system_message = SystemMessage(content=SYSTEM_MESSAGE)
            user_message = UserMessage(content=[
                USER_MESSAGE.format(iterations_history=actions_history),
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
            
            return result.content
        else: 
            logger.debug("??????? What has happened ???????")
            return "No iterations history available."

        