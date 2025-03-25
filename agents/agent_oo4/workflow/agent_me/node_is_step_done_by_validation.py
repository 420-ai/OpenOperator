from core.clients.llm import LLMClient
from core.models import Message, TextContent, ImageContent, LLMResponse, ToolResult, ToolCall
from core.state import State
from core.tracker import Tracker
from agent_oo4.helpers import fm

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

        self.llm = LLMClient("azure", model="gpt-4o-mini", deployment="gpt-4o-mini-deployment")
        # self.llm = LLMClient("ollama", model="llama3.2-vision:latest")

    async def execute(self, validation: str) -> bool:
        logger.debug("Executing...")

        # Messages
        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(
            role="user", 
            content= USER_MESSAGE.format(validation=validation)
        )

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message.model_dump()),
            ("user_message", user_message.model_dump())
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
        
        return detect_boolean_value(result.message.content)
    

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