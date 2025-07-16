import json
from typing import List
from state import State
from tracker import Tracker
from clients.llm import llm_gpt4o, calculate_cost
from clients.som import omniparser
from helpers import encode_image, format_messages, fm
from environment.computer.env import ComputerEnv

import logging
logger = logging.getLogger("agent_me--agent_computer")

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


class OOAgentComputer:
    """
    Agent that take actions in the computer environment
    """

    def __init__(self, state: State, tracker: Tracker, env: ComputerEnv):
        logger.debug("Initializing...")

        self.name = "agent_me--agent_computer"
        self.description = "This agent take actions in the computer environment."

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker

        self.llm = llm_gpt4o
        self.som = omniparser

        self.computerEnv = env

    async def run(self) -> List[dict]:
        logger.debug("Running ...")

        # ----------------------
        # ----------------------
        # ACTIONS LOOP
        # ----------------------
        # ----------------------
        all_messages = []

        # Get the plan step from state
        plan_step = self.state.current_plan_data["plan_step"]["text"]

        # Take screenshot
        screenshot_t1 = self.state.get_current_plan_image("t1")
        screenshot_t1_resized = self.state.get_current_plan_image("t1_resized")
        
        # Analyze the screenshot and get the UI elements
        parsed = self.som.analyze_image(screenshot_t1)

        # region Log + State + Tracker
        self.tracker.save(f"{self.name}-{0}", [
            ("plan_step", plan_step),
            ("screenshot_t1_resized", screenshot_t1_resized)
        ])
        # endregion

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
        all_messages.append(system_message)
        all_messages.append(user_message)

        # region Log + State + Tracker
        self.tracker.save(f"{self.name}-{0}", [
            ("system_message", system_message),
            ("user_message", user_message),
            ("parsed_screenshot", parsed["parsed_image"])
        ])
        # endregion


        loop_count = 0
        while loop_count < self.config.workflow.params.max_plan_step_actions:
            loop_count += 1

            logger.debug("--------------------------")
            logger.debug(f"Agent - Loop count: {loop_count}")
            logger.debug("--------------------------")
            
            # region Log + State + Tracker
            self.tracker.save(f"{self.name}-{loop_count}", [
                ("messages", all_messages)
            ])
            # endregion

            # Call LLM
            result = self.llm.call(
                messages=all_messages,
                tools=TOOLS # CUSTOM TOOLS
            )

            # ---- COST CALCULATION ----
            total_cost = calculate_cost(result.usage, self.llm.model, self.config)
            # ---- END COST CALCULATION ----

            # region Log + State + Tracker
            logger.debug(f"Model: {self.llm.model}, Total cost: {total_cost}$")
            logger.debug(fm(result.message or result.tool_calls))

            # logger.debug(result.tool_calls)
            # logger.debug(result.tool_calls_json)

            self.tracker.save(f"{self.name}-{loop_count}", [
                ("llm_response", result.message or result.tool_calls_json),
                ("cost", f"{total_cost}$"),
            ])
            # endregion

            # ------------------------------
            # Section where we got from LLM a text response
            # => custom implementation of TextMessageTermination
            # ------------------------------
            if result.finish_reason != "tool_calls":
                all_messages.append(result.raw_message.model_dump())
                logger.debug("TextMessageTermination, end the loop")
                break

            
            # Add tool_call to the list of messages
            all_messages.append(result.raw_message.model_dump())
            # message_json = json.loads(result.tool_calls_json)
            # for tc in result.tool_calls:
            #     all_messages.append(tc.model_dump())
            

            # ------------------------------
            # Section where we got from LLM a list of function calls
            # => everything is ok, continue
            # ------------------------------
            actions_json = []
            for tool_call in result.tool_calls:
                action_json = {
                    "id": tool_call.id,
                    "action": tool_call.function.name,
                    "parameters": json.loads(tool_call.function.arguments),
                }
                actions_json.append(action_json)

            logger.debug(f"Actions: \n{actions_json}")

            # ----------------------
            # ----------------------
            # Take actions in the environment
            # ----------------------
            # ----------------------
            # Loop through messages and actions
            for action in actions_json:
                # Take action in the environment
                action_type = str(action["action"])
                params = json.dumps(action["parameters"])

                data = (action_type, params)
                obs, reward, terminated, truncated, info = self.computerEnv.step(data)

                # Add the tool_call result to the list of messages
                msg = {
                    "role": "tool",
                    "tool_call_id": action["id"],  
                    "name": action["action"],
                    "content": info["tool_result"],  
                }
                all_messages.append(msg)

        print("-------------------------")
        print("-------------------------")
        print("-------------------------")
        print("-------------------------")
        print("-------------------------")
        print("-------------------------")
        print("-------------------------")
        print("-------------------------")
        print("We break out of the plan step actions loop")
        print("AGENT TAKE ACTIONS - FINISHED")

        # region Log + State + Tracker
        logger.debug("All messages:")
        logger.debug(format_messages(all_messages))

        self.tracker.save(self.name, [
            ("all_messages", all_messages),
        ])
        # endregion

        return format_messages(all_messages)

        
    
