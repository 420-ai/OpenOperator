import logging
from typing import Any, AsyncGenerator, List, Sequence
from agent.clients.llm.azure_openai import llm_gpt4o
from agent.clients.computer.server_client import get_screenshot
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage, MultiModalMessage, ToolCallRequestEvent, ToolCallExecutionEvent, ToolCallSummaryMessage, ThoughtEvent, ModelClientStreamingChunkEvent
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core.models import UserMessage, SystemMessage
from autogen_core import Image
from agent.helpers import encode_image, resize_and_compress_image, format_task_result
from autogen_agentchat.utils import content_to_str
from tracker import Tracker
from config import OOConfig
from autogen_agentchat.base import TaskResult

logger = logging.getLogger("agent.summarization")

SYSTEM_MESSAGE = """You are an assistant responsible for summarizing the actions taken by an autonomous agent during task execution. 
Your goal is to provide a clear and concise summary of the actions taken and the outcomes observed, based on the provided task, messages, and result. 
If the task was successful, return 'SUCCESS' for the summary. 
If the task failed, provide a factual and detailed summary of the actions and their outcomes. 
Provide the most probable reason, why the task failed.
"""

USER_MESSAGE = """Task: 
===
{plan_task}
===

Result: 
===
{actions_history}
===

Summarize the following messages to clearly outline what actions were taken and their outcomes. 
Highligh the main reason that led to the failure of the task, if applicable."""

class OOSummarizationAgent(BaseChatAgent):

    def __init__(self, config: OOConfig, tracker: Tracker, actions: TaskResult):
        logger.debug("Initializing...")

        name = "agent_summarization"
        description = "Agent responsible for summarizing the actions taken by an autonomous agent during task execution."

        self.config = config
        self.llm = llm_gpt4o
        self.tracker = tracker

        self.actions = actions

        super().__init__(
            name, 
            description,
        )
        
    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return (TextMessage,)

    async def _inner_on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Any:
        self.tracker.set_entity_step(self.name)
        
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name} - Global Step: {self.tracker.step_counter}")
        logger.debug("=================================")

        logger.info("Predicting ...")

        # Get the plan task
        plan_task = messages[0].content

        # Process the actions history
        result_str = format_task_result(self.actions)

        print("==================")
        print("Actions history:")
        print(result_str)
        print("==================")
        
        # Define new messages
        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        self.tracker.save_system_message(system_message)

        user_message = UserMessage(content=[
            USER_MESSAGE.format(plan_task=plan_task, actions_history=result_str), 
        ], source="user")
        self.tracker.save_user_message(user_message)
        
        # Call LLM
        result = await self.llm.create(messages=[
            system_message,
            user_message,
        ])

        # print("==================")
        # print("Result:")
        # print(result)
        # print("==================")

        # Construct response message
        response_message = TextMessage(content=result.content, source=self.name)
        self.tracker.save_response(response_message)

        return response_message

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        result = await self._inner_on_messages(messages, cancellation_token)
        return Response(chat_message=result)
    
    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        result = await self._inner_on_messages(messages, cancellation_token)
        yield Response(
            chat_message=result,
            inner_messages=[],
        )

    async def on_reset(self, cancellation_token):
        return await super().on_reset(cancellation_token)
    

def init_agent_summarization(config: OOConfig, tracker: Tracker, actions: TaskResult) -> OOSummarizationAgent:
    logger.debug("Initializing agent-summarization...")

    agent = OOSummarizationAgent(config, tracker, actions)
    return agent