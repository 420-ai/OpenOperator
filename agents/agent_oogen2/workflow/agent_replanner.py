from typing import Any, AsyncGenerator, Sequence
from workflow.clients.llm import llm_gpt4o, calculate_cost
from workflow.clients.computer import ComputerClient
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage, MultiModalMessage
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core.models import UserMessage, SystemMessage
from autogen_core import Image as AutogenImage
from tracker import Tracker
from config import OOConfig
from state import State
from helpers import format_autogen_message, resize_and_compress_image

import logging
logger = logging.getLogger("agent_replanner")

SYSTEM_MESSAGE = """You are the “Replanner,” responsible for updating or finalizing the plan to achieve the user's objective. Your task is to analyze the provided information, including the objective, the original plan, completed steps, and a screenshot. Based on your analysis, decide whether further actions are needed or if the objective has been fully achieved.

### Core Principles:
1. **Clarity**: Each step must be specific, unambiguous, and self-contained.
2. **Relevance**: Focus only on the essential actions required to achieve the user’s objective.
3. **Context Awareness**: Each step should provide enough information for the agent to understand the goal without additional clarification.
4. **Complete steps**: Make sure you have completed **ALL** steps in order to achieve the objective.
5. **Validation**: Ensure that the final plan is correct and that the objective has been **fully** achieved. (ex. If the user wants to open a file, ensure that the file is open and visible.)

### Agent Capabilities:
The agent has access to the following tools:
- **Mouse Move**: To move the mouse to a specific location on the screen.
- **Mouse Left Click**: To perform a single left-click with the mouse.
- **Mouse Double Click**: To perform a double-click with the mouse.
- **Mouse Scroll**: To scroll up or down on the screen.
- **Keyboard**: To type text, press keys, or execute hotkey combinations.

### Replanner Instructions:
1. **Interpret the User's Objective**: Understand the task and break it down into logical, sequential actions.
2. **Generate Step-by-Step Actions**: 
    - Write concise steps that align with the agent’s capabilities. Ensure each step is actionable and self-contained.
    - Each step must be fully self-contained and should not include substeps (e.g., a, b, c).
    - Each numbered step must describe a complete action, including necessary interactions (e.g., moving the mouse, clicking, typing).
    - Avoid breaking a single logical action into multiple substeps—ensure each step is atomic but complete.
3. **Avoid Explicit Capture or Validation**: Assume the agent will handle capture and validation phases internally. Focus solely on specifying the required action.
4. **Be Direct and Unambiguous**: Clearly define the action, the target UI element, and the intended result.
5. **Minimize Complexity**: Provide only the essential steps to complete the task without unnecessary elaboration.
6. **Analyze Past steps Summarizations**: Review the summarizations of past steps to determine the nature of issues encountered (if any):
   - **Minor Issue**: Retry the step with adjustments, if necessary.
   - **Major Issue**: Modify the plan to address the problem or propose an alternate approach. => Come up with a novel approach if needed.

### Output Format:
1. **Visual Description**: Provide a concise description of what is visible in the screenshot.
2. **Action**: Choose one of the following:
   - **Plan**: List the remaining steps required to complete the objective, ensuring that each action is fully described in a single numbered step with no substeps.
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

USER_MESSAGE = """
Please evaluate the provided information and decide whether the user’s objective has been fully achieved or if additional steps are required.
If additional steps are needed, carefully analyse result of last step and decide if the plan needs to be modified or if a new approach is required.
If the last step contains useful information for the new plan, include it in the plan.

**Objective**:  
===
{objective}  
===

**Original Plan**:  
===
{plan}  
===

**Past steps**:  
===
{past_steps}  
===

**Screenshot**:  
[Image Included: A screenshot with the mouse's current position.]

IMPORTANT:
Reply 'ALL DONE' as a response if the objective has been fully achieved.
"""

class OOReplannerAgent(BaseChatAgent):

    def __init__(self, state: State, tracker: Tracker, objective: str, plan: str, past_steps: str):
        logger.debug("Initializing...")

        name = "agent_replanner"
        description = "Agent responsible for replanning"

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_gpt4o

        self.computer = ComputerClient(server_url=f"{self.config.environment.params.server_ip}:{self.config.environment.params.computer_port}")

        self.objective = objective
        self.plan = plan
        self.past_steps = past_steps

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

        # Take a screenshot of the current UI state
        screenshot = self.computer.get_screenshot()
        # Resize and compress the screenshot
        screenshot_resized = resize_and_compress_image(screenshot)

        self.state.save_plan_image(screenshot_resized, "t2.png")
        
        # Define new messages
        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        user_message = UserMessage(content=[
            USER_MESSAGE.format(
                objective=self.objective,
                plan=self.plan,
                past_steps=self.past_steps
            ), 
            AutogenImage.from_pil(screenshot_resized)
        ], source="user")
        
        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message)
        ])
        # endregion
        
        result = await self.llm.create(
            messages=[
                system_message,
                user_message,
            ]
        )

        # ---- COST CALCULATION ----
        model_name, total_cost = calculate_cost(result.usage, self.llm._resolved_model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Model: {model_name}, Total cost: {total_cost}$")
        logger.debug(format_autogen_message(result))

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
    
def init_agent_replanner(state: State, tracker: Tracker, objective: str, plan: str, past_steps: str) -> OOReplannerAgent:
    logger.debug("Initializing agent-replanner...")
    return OOReplannerAgent(state, tracker, objective, plan, past_steps)