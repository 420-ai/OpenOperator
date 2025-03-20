import json
from typing import Any, List, Union
from config import OOConfig
from state import State
from tracker import Tracker
from clients.llm import my_llm_gpt4o, my_calculate_cost
from clients.som import omniparser
from helpers import encode_image

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

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "keyboard_hotkeys",
            "description": "Simulates pressing a sequence of hotkeys.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hotkeys": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of hotkeys to press (e.g., ['cmd', 'a'])."
                    }
                },
                "required": ["hotkeys"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "keyboard_type",
            "description": "Types text using the keyboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to type on the keyboard."
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_double_click",
            "description": "Performs a double-click with the mouse.",
            "parameters": {
                "type": "object",
                "properties": {}
            },
            "required": []
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_left_click",
            "description": "Performs a left-click with the mouse.",
            "parameters": {
                "type": "object",
                "properties": {}
            },
            "required": []
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_move",
            "description": "Moves the mouse to a specific absolute screen coordinate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "The x coordinate (absolute) to move to."
                    },
                    "y": {
                        "type": "integer",
                        "description": "The y coordinate (absolute) to move to."
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_scroll",
            "description": "Performs a scrolling action in the specified direction ('up', 'down', 'left', or 'right').",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down", "left", "right"],
                        "description": "Determines the direction of scrolling."
                    },
                    "amount": {
                        "type": "integer",
                        "description": "The scroll amount. Positive values move in the natural direction."
                    },
                    "delay": {
                        "type": "number",
                        "description": "Delay (in seconds) between consecutive scrolls. Default is 0."
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Number of times to apply the scroll for smoother motion."
                    }
                },
                "required": ["direction", "amount", "delay", "steps"]
            }
        }
    }
]


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

        self.llm = my_llm_gpt4o
        self.som = omniparser

    async def execute(self, messages: List[Any]) -> Union[str, list]:
        logger.debug("Executing...")

        print(" !!!!! ")
        print (" USE the messages")
        print(messages)

        # Get the plan step from state
        plan_step = self.state.current_plan_data["plan_step"]["text"]
        # Get the screenshot from state
        screenshot_t1 = self.state.get_current_plan_image("t1")
        
        # Analyze the screenshot and get the UI elements
        parsed = self.som.analyze_image(screenshot_t1)

        system_message = {"role": "system", "content": SYSTEM_MESSAGE}
        user_message = {
            "role": "user", 
            "content":  [
                {
                    "type": "text",
                    "text": USER_MESSAGE.format(
                                plan_step=plan_step,
                                ui_elements=parsed["parsed_content_list"]
                            )
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encode_image(parsed["parsed_image"])}",
                    }
                }
            ]
        }

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message),
            ("user_message", user_message),
            ("parsed_screenshot", parsed["parsed_image"])
        ])
        # endregion

        # Call LLM
        result = self.llm.call(
            messages=[
                system_message,
                user_message
            ],
            tools=TOOLS # CUSTOM TOOLS
        )

        

        # ---- COST CALCULATION ----
        model_name, total_cost = my_calculate_cost(result.usage.prompt_tokens, result.usage.completion_tokens, self.llm.model, self.config)
        # ---- END COST CALCULATION ----

        # region Log + State + Tracker
        logger.debug(f"Model: {model_name}, Total cost: {total_cost}$")
        logger.debug(result.to_json())

        self.tracker.save(self.name, [
            ("llm_response", result.to_json()),
            ("cost", f"{total_cost}$"),
        ])
        # endregion

        # ?????
        if len(result.choices) > 1:
            print(result.choices)
            raise ValueError("Multiple choices returned, expected only one. -------> INVESTIGATE")

        # ------------------------------
        # Section where we got from LLM a text response
        # => custom implementation of TextMessageTermination
        # ------------------------------
        if result.choices[0].finish_reason != "tool_calls":
            return result, None

        # ------------------------------
        # Section where we got from LLM a list of function calls
        # => everything is ok, continue
        # ------------------------------
        result_json = []
        for tool_call in result.choices[0].message.tool_calls:
            tool_call_json = {
                "id": tool_call.id,
                "action": tool_call.function.name,
                "parameters": json.loads(tool_call.function.arguments),
            }
            result_json.append(tool_call_json)

        # print("main_with_tools.py 2")
        # print(type(result_json))
        # print(type(result_json[0]))
        # print(result_json)

        return result, result_json
    
