from typing import Any
from config import OOConfig
from state import State
from workflow.clients.llm.local_ollama import llm_phi4
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage
import logging
logger = logging.getLogger("agent.me-node.summarize_plan_step")

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

    def __init__(self, config: OOConfig, state: State):
        logger.debug("Initializing...")

        self.state = state
        self.config = config

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

            summarization = await self.llm.create(
                messages=[
                    SystemMessage(content=SYSTEM_MESSAGE),
                    UserMessage(content=[
                        USER_MESSAGE.format(iterations_history=actions_history),
                    ], source="user")
                ]
            )
            
            return summarization.content
        else: 
            logger.debug("??????? What has happened ???????")
            return "No iterations history available."

        