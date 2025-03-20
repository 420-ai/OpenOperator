import logging
from typing import Any, AsyncGenerator, List, Sequence
from workflow.clients.llm import llm_gpt4o, calculate_cost
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage, MultiModalMessage, ToolCallRequestEvent, ToolCallExecutionEvent, ToolCallSummaryMessage, ThoughtEvent, ModelClientStreamingChunkEvent
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core.models import UserMessage, SystemMessage
from tracker import Tracker
from autogen_agentchat.base import TaskResult
from state import State
from helpers import format_autogen_message, format_task_result

logger = logging.getLogger("agent_summarization")

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

    def __init__(self, state: State, tracker: Tracker, actions: TaskResult):
        logger.debug("Initializing...")

        name = "agent_summarization"
        description = "Agent responsible for summarizing the actions taken by an autonomous agent during task execution."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_gpt4o

        self.actions = actions

        super().__init__(
            name, 
            description,
        )
        
    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return (TextMessage,)

    async def _inner_on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Any:
        
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
        logger.info("Predicting ...")

        # Get the plan task
        plan_task = messages[0].content

        # Process the actions history
        result_str = format_task_result(self.actions)

        
        # Define new messages
        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        user_message = UserMessage(content=[
            USER_MESSAGE.format(plan_task=plan_task, actions_history=result_str), 
        ], source="user")
        
        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message)
        ])
        # endregion

        # Call LLM
        result = await self.llm.create(messages=[
            system_message,
            user_message,
        ])

        # ---- COST CALCULATION ----
        model_name, total_cost = calculate_cost(result.usage, self.llm._resolved_model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Model: {model_name}, Total cost: {total_cost}$")
        logger.debug(format_autogen_message(result))

        self.state.save_plan_text(result.content)

        self.tracker.save(self.name, [
            ("llm_response", result),
            ("cost", f"{total_cost}$"),
        ])
        # endregion

        # Construct response message
        return TextMessage(content=result.content, source=self.name)

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
    

def init_agent_summarization(state: State, tracker: Tracker, actions: TaskResult) -> OOSummarizationAgent:
    logger.debug("Initializing agent-summarization...")
    return OOSummarizationAgent(state, tracker, actions)