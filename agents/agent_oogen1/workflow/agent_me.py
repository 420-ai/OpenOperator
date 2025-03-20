import logging
from typing import AsyncGenerator, Sequence
from workflow.clients.llm import llm_gpt4o
from workflow.clients.computer import ComputerClient
from workflow.clients.som.omniparser import omniparser
from workflow.helpers import resize_and_compress_image
from workflow.tools.keyboard_type import keyboard_type
from workflow.tools.keyboard_hotkeys import keyboard_hotkeys
from workflow.tools.mouse_move import mouse_move
from workflow.tools.mouse_scroll import mouse_scroll
from workflow.tools.mouse_left_click import mouse_left_click
from workflow.tools.mouse_double_click import mouse_double_click
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_agentchat.conditions import TextMessageTermination, HandoffTermination, MaxMessageTermination
from autogen_core import Image
from autogen_core.models import UserMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from tracker import Tracker
from config import OOConfig
from state import State

logger = logging.getLogger("agent.me")

SYSTEM_MESSAGE = """
You are the 'Desktop AI master', an advanced autonomous agent capable of performing any task on a computer efficiently and precisely.

- Execute tasks confidently and without hesitation.
- IMPORTANT: Do not ask questions. Proceed with the task and learn from mistakes.
- Prioritize accuracy, speed, and logical reasoning.
- Follow the user's instructions exactly as given.
- Interact with UI elements by analyzing the provided UI data.
- If necessary, simulate human interactions such as clicking, typing, or navigating windows.

Your goal is to complete each assigned task as efficiently as possible.
"""

USER_MESSAGE = """" 
Your goal is: {objective}

Proceed step by step and ensure the task is completed successfully.
"""

PARSED_UI_ELEMENTS_MESSAGE = """" 
Here are the detected UI elements on the screen, including their coordinates:

=======================================
{parsed_ui_elements}
=======================================

### Interaction Instructions
- To click an element, compute the center coordinates using:   centerX = x + (width / 2), centerY = y + (height / 2)
- To type or input text, locate a relevant text field from the parsed elements.
- If an element is interactive ('interactivity': true), prioritize using it for interaction.
"""

class OOMeAgent(AssistantAgent):
    def __init__(self, state: State, tracker: Tracker, **kwargs):
        logger.debug("Initializing...")

        name = "agent_me"
        description = "Agent representing a user controlling computer"
        
        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_gpt4o
        self.som = omniparser

        self.computer = ComputerClient(server_url=f"{self.config.environment.params.server_ip}:{self.config.environment.params.computer_port}")

        tools = [
            keyboard_type,
            keyboard_hotkeys,
            mouse_move,
            mouse_scroll,
            mouse_left_click,
            mouse_double_click,
        ]

        self.step_counter = 0

        super().__init__(
            name=name, 
            description=description,
            model_client=llm_gpt4o, 
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
        logger.debug(f"Entity: {self.name} | Local Step: {self.step_counter}")
        logger.debug("=================================")
        logger.info("Predicting ...")
        logger.debug(f"Messages: {messages}")

        # Take a screenshot
        screenshot_t1 = self.computer.get_screenshot()

        # Analyse the screenshot
        screenshot_analysis = self.som.analyze_image(screenshot_t1)
        self.state.save_plan_image(screenshot_analysis["parsed_image"], "t1_parsed.png")

        # Resize and compress the screenshot
        parsed_image_resized = resize_and_compress_image(screenshot_analysis["parsed_image"])
        self.state.save_plan_image(parsed_image_resized, "t1_parsed_resized.png")


        final_messages = []
        if(len(messages) > 0):
            # Get the original user task
            user_feedback = messages[0].content
            final_messages.append(user_feedback)

        # Add the parsed UI elements and image to the final messages
        final_messages.append(PARSED_UI_ELEMENTS_MESSAGE.format(parsed_ui_elements=screenshot_analysis["parsed_content_list"]))
        # Add the parsed image to the final messages
        final_messages.append(Image.from_pil(parsed_image_resized))

        user_message = UserMessage(content=final_messages, source="user")

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("screenshot_t1_parsed_resized", parsed_image_resized),
            ("system_message", SYSTEM_MESSAGE),
            ("user_message", user_message)
        ])
        # endregion

        response_counter = 0
        async for response in super().on_messages_stream([user_message], cancellation_token):
            
            # Increment the response counter
            response_counter += 1

            # region Log + State + Tracker
            self.tracker.save(self.name, [
                ("response", response),
            ])
            # endregion

            yield response


def init_agent_me(state: State, tracker: Tracker) -> RoundRobinGroupChat:
    logger.debug("Initializing agent-me team...")

    # Agent
    agent_me = OOMeAgent(
        state=state, 
        tracker=tracker
    )

    config = state.get_config()

    max_messages_termination = MaxMessageTermination(max_messages=config.workflow.params.max_plan_step_actions)
    text_termination = TextMessageTermination(agent_me.name)
    termination = max_messages_termination | text_termination

    # Team 
    team = RoundRobinGroupChat(
            [agent_me],
            termination_condition=termination
        )
    return team