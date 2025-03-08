import logging
from typing import AsyncGenerator, Sequence
from agent.clients.llm.azure_openai import llm
from agent.clients.computer.server_client import get_screenshot
from agent.clients.som.omniparser import OmniparserClient
from agent.helpers import resize_and_compress_image
from agent.tools.keyboard_type import keyboard_type
from agent.tools.keyboard_hotkeys import keyboard_hotkeys
from agent.tools.mouse_move import mouse_move
from agent.tools.mouse_scroll import mouse_scroll
from agent.tools.mouse_left_click import mouse_left_click
from agent.tools.mouse_double_click import mouse_double_click
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core import Image
from autogen_core.models import UserMessage
from tracker import Tracker
from config import OOConfig

logger = logging.getLogger("agent.me")

class OOMeAgent(AssistantAgent):
    def __init__(self, config: OOConfig, tracker: Tracker, **kwargs):
        logger.debug("Initializing...")

        name = "agent_me"
        description = "Agent representing a user controlling computer"
        
        self.config = config
        self.llm = llm
        self.som = OmniparserClient()

        tools = [
            keyboard_type,
            keyboard_hotkeys,
            mouse_move,
            mouse_scroll,
            mouse_left_click,
            mouse_double_click,
        ]

        self.step_counter = 0
        self.tracker = tracker

        super().__init__(
            name=name, 
            description=description,
            model_client=llm, 
            tools=tools, 
            system_message=config.SYSTEM_MESSAGE,
            **kwargs
        )

    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        
        # Increment the step counter
        self.step_counter += 1
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Step: {self.step_counter}")
        logger.debug("=================================")
        self.tracker.set_step(self.step_counter)

        # all history messages
        await self.tracker.save_messages(self._model_context)

        # Take a screenshot
        screenshot = get_screenshot()
        self.tracker.save_origin_screenshot(screenshot)

        # Analyse the screenshot
        screenshot_analysis = self.som.analyze_image(screenshot)
        self.tracker.save_screenshot_analysis(screenshot_analysis)

        # Resize and compress the screenshot
        parsed_image_resized = resize_and_compress_image(screenshot_analysis["parsed_image"])
        self.tracker.save_resized_screenshot(parsed_image_resized)

        final_messages = []
        if(len(messages) > 0):
            # Get the original user task
            user_feedback = messages[0].content
            final_messages.append(user_feedback)

        # Add the parsed UI elements and image to the final messages
        final_messages.append(self.config.PARSED_UI_ELEMENTS_MESSAGE.format(parsed_ui_elements=screenshot_analysis["parsed_content_list"]))
        # Add the parsed image to the final messages
        final_messages.append(Image.from_pil(parsed_image_resized))

        user_message = UserMessage(content=final_messages, source="user")
        self.tracker.save_user_message(user_message)

        response_counter = 0
        async for response in super().on_messages_stream([user_message], cancellation_token):
            
            # Increment the response counter
            response_counter += 1

            self.tracker.save_response(response, response_counter)

            yield response
