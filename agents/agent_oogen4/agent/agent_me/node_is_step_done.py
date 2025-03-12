from config import OOConfig
from state import State
from agent.clients.llm.azure_openai import llm_gpt4o_mini
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage

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

    def __init__(self, config: OOConfig, state: State):
        self.state = state
        self.config = config

        self.llm = llm_gpt4o_mini

    async def execute(self) -> bool:

        plan_step = self.state.current_plan_data["plan_step"]["text"]
        screenshot_t0 = self.state.get_current_plan_image("t0")

        first_step = await self.llm.create(
            messages=[
                SystemMessage(content=SYSTEM_MESSAGE),
                UserMessage(content=[
                    USER_MESSAGE.format(plan_step=plan_step),
                    AutogenImage.from_pil(screenshot_t0) 
                ], source="user")
            ]
        )
        
        return first_step.content