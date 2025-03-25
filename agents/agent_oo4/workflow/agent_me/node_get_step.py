from core.clients.llm import LLMClient
from core.models import Message, TextContent, ImageContent, LLMResponse, ToolResult, ToolCall
from core.state import State
from core.tracker import Tracker
from agent_oo4.helpers import fm

import logging
logger = logging.getLogger("agent_me--node_get_step")

SYSTEM_MESSAGE = """
You are a helpful assistant that helps the user to get the first step of the plan. Do not elaborate on the plan, just return the first step. Do not add any additional information.
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

        self.llm = LLMClient("ollama", model="mistral:latest")


    async def execute(self) -> None:
        logger.debug("Executing...")

        # Get the plan from state
        plan = self.state.current_plan_data["plan_text"]

        # system_message = {"role": "system", "content": SYSTEM_MESSAGE}
        # user_message = {
        #     "role": "user", 
        #     "content":  USER_MESSAGE.format(plan=plan)
        # }

        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(role="user", content=USER_MESSAGE.format(plan=plan))

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message.model_dump()),
            ("user_message", user_message.model_dump())
        ])
        # endregion

        # LLM call
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
        
        self.state.save_plan_step_text(result.message.content)

        self.tracker.save(self.name, [
            ("llm_response", result.message.content),
            ("cost", cost),
        ])
        # endregion
        