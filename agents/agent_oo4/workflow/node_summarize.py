from core.clients.llm import LLMClient
from core.models import Message
from core.state import State
from core.tracker import Tracker
from agent_oo4.helpers import fm

import logging
logger = logging.getLogger("node_summarize")

SYSTEM_MESSAGE = """You are a summarizer agent. Your task is to create a concise and clear summary of the actions taken.
"""

USER_MESSAGE = """Here are the actions taken by the agent:
{history}
"""


class OONodeSummarize:

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "node_summarize"
        self.description = "Node responsible for summarizing the actions taken by the agent."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        # self.llm = LLMClient("azure", model="gpt-4o", deployment="gpt-4o-deployment")
        self.llm = LLMClient("ollama", model="mistral:latest")


    async def execute(self) -> str:
        
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
        logger.debug("Executing...")

        # ----------------------
        # Format all steps taken in the plan
        # ----------------------
        result = self.state.get_all_plan_versions_data()

        history = ""
        for outer_key, inner_dict in result.items():
            history += f"=== Version {outer_key} ===\n"
            for inner_key, inner_value in inner_dict.items():
                if inner_key == "plan_step_text":
                    history += f"Plan step: {inner_value}\n"
                elif inner_key == "plan_step_result":
                    history += f"Result: {inner_value}\n"

        # ----------------------
        # Summarize
        # ----------------------
        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(
            role="user", 
            content=USER_MESSAGE.format(history=history)
        )

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message.model_dump()),
            ("user_message", user_message.model_dump())
        ])
        # endregion
        
        # Call LLM
        result = self.llm.call(messages=[
            system_message,
            user_message,
        ])

        # region Log + State + Tracker
        cost = f"Provider: {self.llm.provider}, Model: {self.llm.model}, Total cost: {result.usage.cost}$"
        logger.debug(cost)
        logger.debug(fm(result.message.content))

        self.tracker.save(self.name, [
            ("llm_response", result.message.content),
            ("cost", cost),
        ])
        # endregion

        return result.message.content
