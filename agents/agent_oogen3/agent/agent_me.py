import logging
from typing import AsyncGenerator, Sequence
from agent.clients.llm.azure_openai import llm
from agent.clients.som.omniparser import OmniparserClient
from agent.tools.keyboard_type import keyboard_type
from agent.tools.keyboard_hotkeys import keyboard_hotkeys
from agent.tools.mouse_move import mouse_move
from agent.tools.mouse_scroll import mouse_scroll
from agent.tools.mouse_left_click import mouse_left_click
from agent.tools.mouse_double_click import mouse_double_click
from agent.tools.find_ui_element import find_ui_element
from agent.tools.capture_state_before_action import capture_state_before_action
from agent.tools.validate_objective_via_screenshot import validate_objective_via_screenshot
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMessageTermination, HandoffTermination, MaxMessageTermination
from autogen_agentchat.base import Handoff
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core import Image
from autogen_core.models import UserMessage
from tracker import Tracker
from config import OOConfig

logger = logging.getLogger("agent.me")

SYSTEM_MESSAGE = """"
You are `AgentME`, an AI agent responsible for executing **one specific action at a time** within a UI automation workflow. Your role is to follow the provided step, interact with the UI, and return the outcome.

### Execution Process:
1. **Capture state before action**: Capture UI state before executing action.
2. **Perform the Action**: Execute the step precisely using available tools (Mouse Move, Click, Keyboard).
3. **Validate Execution**: Confirm whether the expected result has occurred.
4. **Report Outcome**:
   - **Success:** If the step executed correctly, return "Step Completed."
   - **Failure:** If the action cannot be performed, return the reason.

### Agent Capabilities:
- Mouse Move, Click, Double Click, Scroll
- Keyboard Input
- Find UI Element
- Capture State Before Action
- Validate Objective via Screenshot

### Expected Output:
- "Step Completed" if successful.
- "Step Failed: [Reason]" if the action cannot be performed.
"""

USER_MESSAGE = """For the following plan:
{plan_str}

GOAL: Execute **only** the step: {task}

VALIDATION: After performing the action, check if the UI state matches the expected outcome.

FINISH: Return the result (Success/Failure). Do not proceed to the next step.
"""

class OOMeAgent(AssistantAgent):
    def __init__(self, config: OOConfig, tracker: Tracker, plan: str, **kwargs):
        logger.debug("Initializing...")

        name = "agent_me"
        description = "Agent representing a user controlling computer"
        
        self.config = config
        self.llm = llm
        self.som = OmniparserClient()

        self.plan = plan

        tools = [
            keyboard_type,
            keyboard_hotkeys,
            mouse_move,
            mouse_scroll,
            mouse_left_click,
            mouse_double_click,
            find_ui_element,
            capture_state_before_action,
            validate_objective_via_screenshot
        ]

        self.step_counter = 0
        self.tracker = tracker

        super().__init__(
            name=name, 
            description=description,
            model_client=llm, 
            tools=tools, 
            system_message=SYSTEM_MESSAGE,
            **kwargs
        )

    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        self.tracker.set_entity_step(self.name)
        self.step_counter += 1
        
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name} - Global Step: {self.tracker.step_counter} | Local Step: {self.step_counter}")
        logger.debug("=================================")

        logger.info("Predicting ...")

        # all history messages
        await self.tracker.save_messages(self._model_context)

        final_messages = []
        if(len(messages) > 0):
            # Get the original user task
            final_messages.append(USER_MESSAGE.format(plan_str=self.plan, task=messages[0].content))
        
        user_message = UserMessage(content=final_messages, source="user")
        self.tracker.save_user_message(user_message)

        response_counter = 0
        async for response in super().on_messages_stream([user_message], cancellation_token):
            
            # Increment the response counter
            response_counter += 1

            self.tracker.save_response(response, response_counter)

            yield response

def init_agent_me(config: OOConfig, tracker: Tracker, plan: str) -> RoundRobinGroupChat:
    logger.debug("Initializing agent-me team...")

    # Agent
    agent_me = OOMeAgent(
        config=config, 
        tracker=tracker,
        plan=plan,
    )

    max_messages_termination = MaxMessageTermination(max_messages=5)
    text_termination = TextMessageTermination(agent_me.name)
    termination = max_messages_termination | text_termination

    # Team 
    team = RoundRobinGroupChat(
            [agent_me],
            termination_condition=termination
        )
    return team