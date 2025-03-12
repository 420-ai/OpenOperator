import logging
from typing import AsyncGenerator, Sequence
from agent.clients.llm.azure_openai import llm_gpt4o
from agent.clients.som.omniparser import OmniparserClient
from agent.tools.keyboard_type import keyboard_type
from agent.tools.keyboard_hotkeys import keyboard_hotkeys
from agent.tools.mouse_move import mouse_move
from agent.tools.mouse_scroll import mouse_scroll
from agent.tools.mouse_left_click import mouse_left_click
from agent.tools.mouse_double_click import mouse_double_click
from agent.tools.find_ui_element import find_ui_element
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMessageTermination, HandoffTermination, MaxMessageTermination
from autogen_agentchat.base import Handoff
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core import Image
from autogen_core.models import UserMessage
from state import State
from tracker import Tracker
from config import OOConfig

logger = logging.getLogger("agent.take_actions")

SYSTEM_MESSAGE = """
You are `AgentME`, an AI agent responsible for executing **one specific action at a time** within a UI automation workflow. Your role is to follow the provided step, interact with the UI, and return the outcome.

### Agent Capabilities:
- Mouse Move, Click, Double Click, Scroll
- Keyboard Input
- Find UI Element

### Expected Output:
- "Step Completed" if successful.
- "Step Failed: [Reason]" if the action cannot be performed.
"""

USER_MESSAGE = """
For the following plan:
{plan_str}

GOAL: Execute **only** the step: {task}
"""


class OOAgentTakeActions(AssistantAgent):
    def __init__(self, config: OOConfig, state: State, **kwargs):
        logger.debug("Initializing...")

        name = "agent_take_actions"
        description = "Agent representing a user controlling computer"
        
        self.config = config
        self.state = state

        self.llm = llm_gpt4o
        self.som = OmniparserClient()


        tools = [
            keyboard_type,
            keyboard_hotkeys,
            mouse_move,
            mouse_scroll,
            mouse_left_click,
            mouse_double_click,
            find_ui_element,
        ]

        self.step_counter = 0

        super().__init__(
            name=name, 
            description=description,
            model_client=self.llm, 
            tools=tools, 
            system_message=SYSTEM_MESSAGE,
            **kwargs
        )

    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        self.step_counter += 1
        
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name} - Global Step: {self.tracker.step_counter} | Local Step: {self.step_counter}")
        logger.debug("=================================")

        logger.info("Predicting ...")

        final_messages = []
        if(len(messages) > 0):

            plan = self.state.current_plan_data["plan_text"]
            
            # Get the original user task
            final_messages.append(USER_MESSAGE.format(plan_str=plan, task=messages[0].content))
        
        user_message = UserMessage(content=final_messages, source="user")

        response_counter = 0
        async for response in super().on_messages_stream([user_message], cancellation_token):
            
            # Increment the response counter
            response_counter += 1

            yield response

def init_agent_take_action(config: OOConfig, state: State) -> RoundRobinGroupChat:
    logger.debug("Initializing agent-me team...")

    # Agent
    agent_me = OOAgentTakeActions(
        config=config, 
        state=state,
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