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

from autogen_agentchat.messages import ThoughtEvent, ToolCallRequestEvent, ToolCallExecutionEvent
from autogen_agentchat.base._chat_agent import Response as ChatAgentResponse

from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_core.models import UserMessage, AssistantMessage, SystemMessage, FunctionExecutionResult, FunctionExecutionResultMessage

logger = logging.getLogger("agent.me")


SYSTEM_MESSAGE = """
You are Screen Helper, a world-class reasoning engine that can complete any goal on a computer to help a user.
Do not as any questions, act confidently and quickly.
"""


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
    def __init__(self, tracker: Tracker):
        logger.debug("Initializing...")

        name = "agent_me"
        description = "Agent representing a user controlling computer"
        
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

        tracker.save_system_message(SYSTEM_MESSAGE)

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
        
        # Increment the step counter
        self.step_counter += 1
        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Step: {self.step_counter}")
        logger.debug("=================================")
        self.tracker.set_step(self.step_counter)


        # ------------------------------------------
        # All history messages
        # ------------------------------------------
        # try:
        #     history_messages = await self._model_context.get_messages()

        #     print("-----------------------------------")
        #     print("History messages:")
        #     # print(history_messages)
        #     for message in history_messages:
        #         if isinstance(message, BaseAgentEvent):
        #             print("Message is a BaseAgentEvent instance")
        #             print(type(message))
        #         elif isinstance(message, BaseChatMessage):
        #             print("Message is a BaseChatMessage instance")
        #             print(type(message))

        #         elif isinstance(message, SystemMessage):
        #             print("Message is a SystemMessage instance")
        #             print(type(message))
        #         elif isinstance(message, UserMessage):
        #             print("Message is a UserMessage instance")
        #             print(type(message))
        #         elif isinstance(message, AssistantMessage):
        #             print("Message is an AssistantMessage instance")
        #             print(type(message))
        #         elif isinstance(message, FunctionExecutionResult):
        #             print("Message is a FunctionExecutionResult instance")
        #             print(type(message))
        #         elif isinstance(message, FunctionExecutionResultMessage):
        #             print("Message is a FunctionExecutionResultMessage instance")
        #             print(type(message))

        #         else:
        #             print("Message type not recognized!")
        #     print("-----------------------------------")

        # except Exception as e:
        #     logger.error(f"Failed to save history messages: {e}")


        # ------------------------------------------
        # Memory
        # ------------------------------------------
        # memory_file_path = os.path.join(self.run_dir, "memory.txt")
        # try:
            
        #     print("-----------------------------------")
        #     print("Memory:")
        #     print(self._memory)
        #     print("-----------------------------------")

        #     # memory_content = ""
        #     # if self._memory:
        #     #     for memory in self._memory:
        #     #         mem_state = await memory.save_state()
        #     #         memory_content += json.dumps(mem_state, indent=4) + "\n"
        #     # save_txt(memory_content, STEP_DIR, "memory.txt")
        # except Exception as e:
        #     logger.error(f"Failed to save memory: {e}")


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
            user_task = messages[0].content
            final_messages.append(USER_MESSAGE.format(objective=user_task))
        
        # Add the parsed UI elements and image to the final messages
        final_messages.append(MESSAGE_PARSED_UI_ELEMENTS.format(parsed_ui_elements=screenshot_analysis["parsed_content_list"]))
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
