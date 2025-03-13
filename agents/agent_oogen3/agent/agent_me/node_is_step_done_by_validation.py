from config import OOConfig
from state import State
from agent.clients.llm.azure_openai import llm_gpt4o_mini
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage
import logging
logger = logging.getLogger("agent.me-node.is_step_done_by_validation")

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

    def __init__(self, config: OOConfig, state: State):
        logger.debug("Initializing...")

        self.state = state
        self.config = config

        self.llm = llm_gpt4o_mini

    async def execute(self, validation: str) -> bool:
        logger.debug("Executing...")
        
        isDone = await self.llm.create(
            messages=[
                SystemMessage(content=SYSTEM_MESSAGE),
                UserMessage(content=[
                    USER_MESSAGE.format(validation=validation),
                ], source="user")
            ]
        )
        
        return isDone.content