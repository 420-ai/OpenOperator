from typing import Tuple
from core.clients.llm import LLMClient
from core.models import Message, TextContent, ImageContent, LLMResponse, ToolResult, ToolCall
from core.state import State
from core.tracker import Tracker
from agent_oo4.helpers import encode_image, fm

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

        self.llm = LLMClient("ollama", model="llama3.2-vision:latest")

    async def execute(self) -> Tuple[bool, str]:
        logger.debug("Executing...")
        
        # Get the plan step from state
        plan_step = self.state.current_plan_data["plan_step"]["text"]
        # Get the screenshot from state
        screenshot_t0 = self.state.get_current_plan_image("t0")
        
        # Messages
        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(
            role="user", 
            content=[
                TextContent(type="text", text=USER_MESSAGE.format(plan_step=plan_step)),
                ImageContent(
                    type="image",        
                    data=encode_image(screenshot_t0),
                    media_type="image/png"
                )
            ]
        )

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message.model_dump()),
            ("user_message", user_message.model_dump()),
            ("screenshot_t0", screenshot_t0)
        ])
        # endregion

        result = self.llm.call(
            messages=[
                system_message,
                user_message
            ]
        )

        # region Log + State + Tracker
        cost = f"Provider: {self.llm.provider}, Model: {self.llm.model}, Total cost: {result.usage.cost}$"
        logger.debug(cost)
        logger.debug(fm(result.message.content))

        self.tracker.save(self.name, [
            ("llm_response", result.message.content),
            ("cost", cost),
        ])
        # endregion

        result_boolean = detect_boolean_value(result.message.content)

        return result_boolean, result.message.content

def detect_boolean_value(text):
    text_upper = text.upper()
    
    if "FALSE" in text_upper:
        return False
    elif "TRUE" in text_upper:
        return True
    else:
        return None