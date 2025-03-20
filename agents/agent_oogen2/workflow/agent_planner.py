import logging
from state import State
from typing import Any, AsyncGenerator, List, Sequence
from workflow.clients.llm import llm_gpt4o, calculate_cost
from workflow.clients.computer import ComputerClient
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage, MultiModalMessage
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core.models import UserMessage, SystemMessage
from autogen_core import Image
from helpers import format_autogen_message, resize_and_compress_image
from tracker import Tracker

logger = logging.getLogger("agent_planner")

SYSTEM_MESSAGE = """You are an AI assistant designed to generate precise, actionable, and step-by-step plans for automating tasks. Your role is to help another AI agent execute these plans efficiently by providing clear instructions for each action.

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

### Planner Instructions:
1. **Interpret the User's Objective**: Understand the task and break it down into logical, sequential actions.
2. **Generate Step-by-Step Actions**: 
    - Write concise steps that align with the agent’s capabilities. Ensure each step is actionable and self-contained.
    - Each step must be fully self-contained and should not include substeps (e.g., a, b, c).
    - Each numbered step must describe a complete action, including necessary interactions (e.g., moving the mouse, clicking, typing).
    - Avoid breaking a single logical action into multiple substeps—ensure each step is atomic but complete.
3. **Avoid Explicit Capture or Validation**: Assume the agent will handle capture and validation phases internally. Focus solely on specifying the required action.
4. **Be Direct and Unambiguous**: Clearly define the action, the target UI element, and the intended result.
5. **Minimize Complexity**: Provide only the essential steps to complete the task without unnecessary elaboration.

### Output Format:
1. **Visual Description**: Provide a concise description of what is visible in the screenshot.
2. **Action**: Choose one of the following:
   - **Plan**: Provide the plan as a numbered list, with each step written as a clear, actionable instruction. No substeps.
   - **Response**: Provide the final answer if the objective has been **fully** achieved.

Follow the output format strictly. Example of output:
=====
### Visual Description:  
<VISUAL_DESCRIPTION>

### Action:  

**Plan**:  
1. <STEP_1>  
2. <STEP_2> 
3. <STEP_3>
=====
"""

USER_MESSAGE = """Your objective is: {objective}. Please create a simple, step-by-step plan that an AI agent with the listed tools can follow to complete the objective.
                     
**Screenshot**:  
[Image Included: A screenshot with the mouse's current position.]
"""

class OOPlannerAgent(BaseChatAgent):

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        name = "agent_planner"
        description = "Agent responsible for planning"

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.computer = ComputerClient(server_url=f"{self.config.environment.params.server_ip}:{self.config.environment.params.computer_port}")

        self.llm = llm_gpt4o

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
        self.state.create_new_plan_version()

        # Get the user task
        user_task = messages[0].content
        
        # Take a screenshot
        screenshot_t0 = self.computer.get_screenshot()

        # Resize and compress the screenshot
        screenshot_t0_resized = resize_and_compress_image(screenshot_t0)
        self.state.save_plan_image(screenshot_t0_resized, "t0.png")

        # Define new messages
        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        user_message = UserMessage(content=[
            USER_MESSAGE.format(objective=user_task), 
            Image.from_pil(screenshot_t0_resized)
        ], source="user")
        
        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("screenshot_t0_resized", screenshot_t0_resized),
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

        # [Not needed] Construct response message - 
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
    

def init_agent_planner(state: State, tracker: Tracker) -> OOPlannerAgent:
    logger.debug("Initializing agent-planner...")
    return OOPlannerAgent(state, tracker)