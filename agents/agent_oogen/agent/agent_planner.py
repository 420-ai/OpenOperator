import logging
from typing import Any, AsyncGenerator, List, Sequence
from agent.clients.llm.azure_openai import llm
from agent.clients.computer.server_client import get_screenshot
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage, MultiModalMessage
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core.models import UserMessage, SystemMessage
from autogen_core import Image
from agent.helpers import encode_image, resize_and_compress_image
from autogen_agentchat.utils import content_to_str

logger = logging.getLogger("agent.planner")


SYSTEM_MESSAGE = """You are an AI assistant designed to generate precise, actionable, and step-by-step plans for automating tasks in Microsoft Teams. Your role is to help another AI agent execute these plans efficiently by providing clear instructions for each action.

### Core Principles:
1. **Clarity**: Each step must be specific, unambiguous, and self-contained.
2. **Efficiency**: Avoid redundant or unnecessary actions; each step should directly contribute to completing the task, with respect of Agent capabilities (and his tools).
3. **Relevance**: Focus only on the essential actions required to achieve the user’s objective.
4. **Context Awareness**: Each step should provide enough information for the agent to understand the goal without additional clarification.
5. **Agent Awareness**: Each step should align with the agent's **capture → action → validate** workflow, ensuring seamless execution and validation. 

### Agent Capabilities:
The agent has access to the following tools:
- **Mouse Move**: To move the mouse to a specific location on the screen.
- **Mouse Left Click**: To perform a single left-click with the mouse.
- **Mouse Double Click**: To perform a double-click with the mouse.
- **Mouse Scroll**: To scroll the mouse wheel up or down.
- **Keyboard**: To type text, press keys, or execute hotkey combinations.
- **Python REPL**: To run Python code for calculations or other logic.
- **Capture State**: Captures a screenshot of the current UI state before any action is performed. Useful for reference or comparison purposes.
- **Validate Outcome**: Confirms whether an action achieved the intended result by analyzing a screenshot.
- **Analyze UI Elements**: Captures and analyzes the screen to identify UI elements, their properties, and coordinates.

### Planner Instructions:
1. **Interpret the User's Objective**: Understand the task and break it down into logical, sequential actions.
2. **Generate Step-by-Step Actions**: Write concise steps that align with the agent’s capabilities. Ensure each step is actionable and self-contained.
3. **Avoid Explicit Capture or Validation**: Assume the agent will handle capture and validation phases internally. Focus solely on specifying the required action.
4. **Be Direct and Unambiguous**: Clearly define the action, the target UI element, and the intended result.
5. **Minimize Complexity**: Provide only the essential steps to complete the task without unnecessary elaboration.

### Output Format:
Provide the plan as a numbered list, with each step written as a clear, actionable instruction. Avoid adding explanations, as the output will be consumed directly by the agent.
"""

USER_MESSAGE = """Your objective is: {objective}. Please create a simple, step-by-step plan that an AI agent with the listed tools can follow to complete the objective.
                     
**Screenshot**:  
[Image Included: A screenshot with the mouse's current position highlighted as a red circle (20px).]
"""

class OOPlannerAgent(BaseChatAgent):

    def __init__(self):
        logger.debug("Initializing...")

        name = "OOPlannerAgent"
        description = "Agent responsible for planning"
        super().__init__(name, description)
        
        self.llm = llm

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return (TextMessage,)

    async def _inner_on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Any:
        logger.info("Predicting ...")

        # Get the user task
        user_task = messages[0].content
        
        # Take a screenshot
        screenshot = get_screenshot()

        # Resize and compress the screenshot
        screenshot_resized = resize_and_compress_image(screenshot)

        # Define new messages
        new_messages = [
            SystemMessage(content=SYSTEM_MESSAGE),
            UserMessage(content=[
                USER_MESSAGE.format(objective=user_task), 
                Image.from_pil(screenshot_resized)
            ], source="user")
        ]

        # Call LLM
        result = await self.llm.create(messages=new_messages)

        # Construct response message
        response_message = TextMessage(content=result.content, source=self.name)
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
    
    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass


