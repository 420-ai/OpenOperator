from core.clients.llm import LLMClient
from core.models import Message, TextContent, ImageContent, LLMResponse, ToolResult, ToolCall
from core.state import State
from core.tracker import Tracker
from agent_oo4.helpers import fm

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

        self.llm = LLMClient("ollama", model="mistral:latest")

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


            # Messages
            system_message = Message(role="system", content=SYSTEM_MESSAGE)
            user_message = Message(
                role="user", 
                content=USER_MESSAGE.format(iterations_history=actions_history)
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
            
            return result.message.content
        else: 
            logger.debug("??????? What has happened ???????")
            raise Exception("No iterations history available.")

        