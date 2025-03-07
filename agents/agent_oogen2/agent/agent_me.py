import logging
from typing import Any, AsyncGenerator, Dict, List, Sequence, Tuple
from agent.clients.llm.azure_openai import llm
from agent.clients.computer.server_client import get_screenshot
from agent.clients.som.omniparser import OmniparserClient
from agent.helpers import encode_image, decode_image, resize_and_compress_image
from agent.tools.keyboard_type import keyboard_type
from agent.tools.keyboard_hotkeys import keyboard_hotkeys
from agent.tools.mouse_move import mouse_move
from agent.tools.mouse_scroll import mouse_scroll
from agent.tools.mouse_left_click import mouse_left_click
from agent.tools.mouse_double_click import mouse_double_click
from agent.tools.python_repl import python_repl_tool
from agent.tools.analyse_ui_elements import analyse_ui_elements
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage, MultiModalMessage
from autogen_core import CancellationToken
from autogen_agentchat.base import Response
from autogen_core.models import UserMessage, SystemMessage
from autogen_core import Image
from PIL import Image as PILImage
from autogen_agentchat.utils import content_to_str

logger = logging.getLogger("agent.me")


SYSTEM_MESSAGE = """You are Screen Helper, a world-class reasoning engine that can complete any goal on a computer to help a user"""


USER_MESSAGE = """Your goal is:
!!!!
{objective}
!!!!
"""


MESSAGE_PARSED_UI_ELEMENTS = """
Here are parsed UI elements including their coordinates from the image (attached):
=======================================
{parsed_ui_elements}
=======================================

If you want to click on the element, calculate the center of the element using the formula: centerX = x + (width / 2), centerY = y + (height / 2)
"""


class OOMeAgent(AssistantAgent):
    def __init__(self):
        logger.debug("Initializing...")

        name = "agent_me"
        description = "Agent representing the user controlling computer"
        
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

        super().__init__(
            name=name, 
            description=description,
            model_client=llm, 
            tools=tools, 
            system_message=SYSTEM_MESSAGE
        )

    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:

        # Take a screenshot
        screenshot = get_screenshot()

        # Analyse the screenshot
        screenshot_analysis = self.som.analyze_image(screenshot)

        # Resize and compress the screenshot
        parsed_image_resized = resize_and_compress_image(screenshot_analysis["parsed_image"])

        final_messages = []
        if(len(messages) > 0):
            # Get the original user task
            user_task = messages[0].content
            final_messages.append(USER_MESSAGE.format(objective=user_task))
        
        # Add the parsed UI elements and image to the final messages
        final_messages.append(MESSAGE_PARSED_UI_ELEMENTS.format(parsed_ui_elements=screenshot_analysis["parsed_content_list"]))
        # Add the parsed image to the final messages
        final_messages.append(Image.from_pil(parsed_image_resized))

        user_message = UserMessage(content=final_messages, source="user")

        async for response in super().on_messages_stream([user_message], cancellation_token):
            yield response
