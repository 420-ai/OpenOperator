from config import OOConfig
from state import State
from workflow.clients.llm.local_ollama import llm_phi4
from autogen_core.models import UserMessage, SystemMessage
import logging
logger = logging.getLogger("agent.me-node.get_step")

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

    def __init__(self, config: OOConfig, state: State):
        logger.debug("Initializing...")

        self.state = state
        self.config = config

        self.llm = llm_phi4

    async def execute(self) -> None:
        logger.debug("Executing...")

        # Get the plan from state
        plan = self.state.current_plan_data["plan_text"]

        # Log the plan
        logger.debug("-------------------")
        logger.debug("Plan:")
        logger.debug(plan)
        logger.debug("-------------------")

        # LLM call
        first_step = await self.llm.create(
            messages=[
                SystemMessage(content=SYSTEM_MESSAGE),
                UserMessage(content=[
                    USER_MESSAGE.format(plan=plan), 
                ], source="user")
            ]
        )

        # Log the first step
        logger.debug("-------------------")
        logger.debug("First step:")
        logger.debug(first_step.content)
        logger.debug("-------------------")

        # Save the first step in the state
        self.state.save_plan_step_text(first_step.content)
        