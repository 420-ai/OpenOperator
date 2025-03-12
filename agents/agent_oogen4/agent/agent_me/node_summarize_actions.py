from typing import Any
from config import OOConfig
from state import State
from agent.clients.llm.local_ollama import llm_phi4
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage

SYSTEM_MESSAGE = """
You are AI assistant that is helping summarize actions.
"""

USER_MESSAGE = """
Summarize following actions into short text.

{messages}
"""

class NodeSummarizeActions:
    """
    Summarize actions
    """

    def __init__(self, config: OOConfig, state: State):
        self.state = state
        self.config = config

        self.llm = llm_phi4

    async def execute(self, messages: Any) -> bool:

        summarization = await self.llm.create(
            messages=[
                SystemMessage(content=SYSTEM_MESSAGE),
                UserMessage(content=[
                    USER_MESSAGE.format(messages=messages),
                ], source="user")
            ]
        )
        
        return summarization.content