import logging
from typing import AsyncGenerator, List, Sequence
from agent.llm_clients.azure_openai import llm_client
from agent.som_clients.omniparser import OmniparserClient
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage
from autogen_core import CancellationToken
from autogen_agentchat.base import Response

logger = logging.getLogger("agent.main")

class OOGenAgent(BaseChatAgent):
    def __init__(self):
        logger.debug("Initializing...")

        name = "OOGenAgent"
        description = "Open Operator agent that can control the computer."
        super().__init__(name, description)
        
        self.llm_client = llm_client
        self.som_client = OmniparserClient()

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return (TextMessage,)

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        logger.info("Predicting ...")
        
        # Take a screenshot

        # Analyze the screenshot -> SoM

        # Call LLM

        print(messages)

        return Response(chat_message=TextMessage(content="FUCK"))
    
    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        logger.info("Predicting (streaming) ...")

        # Take a screenshot

        # Analyze the screenshot -> SoM

        # Call LLM

        print(messages)
        
        yield Response(
            chat_message=TextMessage(content="FUCK"),
            inner_messages=[],
        )
    
    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass