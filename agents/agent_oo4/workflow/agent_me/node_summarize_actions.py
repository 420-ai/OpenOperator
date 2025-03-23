from typing import Any, List
from core.clients.llm import LLMClient
from core.models import Message, TextContent, ImageContent, LLMResponse, ToolResult, ToolCall
from core.state import State
from core.tracker import Tracker
from agent_oo4.helpers import fm

import logging
logger = logging.getLogger("agent_me--node_summarize_actions")

SYSTEM_MESSAGE = """
You are an AI assistant that summarizes a sequence of actions into a short, concise summary.

Instructions:
- Only output the summarization itself.
- Do not include any introductory or explanatory text.
- Do not repeat or restate the input.
- Do not speculate or add context.
- Your output must be factual, minimal, and strictly based on the provided actions.

Output format:
<single concise summary, no headings, no lists, no extra commentary>
"""

USER_MESSAGE = """
Goal of the actions:
===========================
{plan_step}
===========================

Actions that occurred:
===========================
{messages}
===========================
"""

class NodeSummarizeActions:
    """
    Summarize actions
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_summarize_actions"
        self.description = "Summarize actions."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = LLMClient("ollama", model="mistral:latest")

    async def execute(self, messages: List[Message]) -> bool:
        logger.debug("Executing...")

        # -------------------------------------
        # Shortening the user messages
        for message in messages:
            if message.role == "user":
                if isinstance(message.content, list):
                    for contentItem in message.content:
                        if isinstance(contentItem, TextContent):
                            cutoff_marker = "\n=========================\n"
                            if cutoff_marker in contentItem.text:
                                contentItem.text = contentItem.text.split(cutoff_marker)[1]
                        if isinstance(contentItem, ImageContent):
                            contentItem.data = "<BASE64_IMAGE>"

        shortened_messages = [m.model_dump() for m in messages]                         
        # -------------------------------------
        
        plan_step = self.state.current_plan_data["plan_step"]["text"]
        
        # Messages
        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(
            role="user", 
            content=USER_MESSAGE.format(plan_step=plan_step, messages=shortened_messages)
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