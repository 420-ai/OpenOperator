from typing import Any, List, Union
from config import OOConfig
from state import State
from tracker import Tracker
from clients.llm import llm_gpt4o, calculate_cost
from clients.som import omniparser
from autogen_core import Image as AutogenImage
from autogen_core.models import UserMessage, SystemMessage
from helpers import format_autogen_message
import json
from workflow.agent_me.node_create_actions.tools.keyboard_type import keyboard_type
from workflow.agent_me.node_create_actions.tools.keyboard_hotkeys import keyboard_hotkeys
from workflow.agent_me.node_create_actions.tools.mouse_move import mouse_move
from workflow.agent_me.node_create_actions.tools.mouse_scroll import mouse_scroll
from workflow.agent_me.node_create_actions.tools.mouse_left_click import mouse_left_click
from workflow.agent_me.node_create_actions.tools.mouse_double_click import mouse_double_click

import logging
logger = logging.getLogger("agent_me--node_create_actions")

SYSTEM_MESSAGE = """
You are an AI assistant responsible for generating a set of automated actions based on a given textual description and an accompanying screenshot. 
"""

USER_MESSAGE = """
Here is the textual description.
=========================
{plan_step}
=========================

Attached is current screenshot including ID of UI elements. Each UI element has a unique ID and you can see their coordinates below.
=========================
{ui_elements}
=========================
"""

class NodeCreateActions:
    """
    Check if the step is done.
    """

    def __init__(self, config: OOConfig, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me--node_create_actions"
        self.description = "This node's responsibility is to generate actions (for environment) based on the plan step."

        self.state = state
        self.config = config
        self.tracker = tracker

        self.llm = llm_gpt4o
        self.som = omniparser

        self.tools = [
            keyboard_type,
            keyboard_hotkeys,
            mouse_move,
            mouse_scroll,
            mouse_left_click,
            mouse_double_click,
        ]

    async def execute(self, messages: List[Any]) -> Union[str, list]:
        logger.debug("Executing...")

        # Get the plan step from state
        plan_step = self.state.current_plan_data["plan_step"]["text"]
        # Get the screenshot from state
        screenshot_t1 = self.state.get_current_plan_image("t1")
        
        # Analyze the screenshot and get the UI elements
        parsed = self.som.analyze_image(screenshot_t1)

        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        user_message = UserMessage(content=[
            USER_MESSAGE.format(
                plan_step=plan_step,
                ui_elements=parsed["parsed_content_list"]
            ),
            AutogenImage.from_pil(parsed["parsed_image"]) 
        ], source="user")

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message),
            ("parsed_screenshot", parsed["parsed_image"])
        ])
        # endregion

        result = await self.llm.create(
            messages=[
                system_message,
                user_message
            ],
            tools=self.tools
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

        # ------------------------------
        # Section where we got from LLM a text response
        # => custom implementation of TextMessageTermination
        # ------------------------------
        print("main_with_tools.py 1")
        print(type(result))
        print(type(result.content))
        print(result.content)

        if type(result.content) == str:
            return result.content, None

        # ------------------------------
        # Section where we got from LLM a list of function calls
        # => everything is ok, continue
        # ------------------------------
        result_json = []
        for func_call in result.content:
            func_call_json = {
                "action": func_call.name,
                "parameters": json.loads(func_call.arguments),
            }
            result_json.append(func_call_json)

        print("main_with_tools.py 2")
        print(type(result_json))
        print(type(result_json[0]))
        print(result_json)

        return result.content, result_json
    
