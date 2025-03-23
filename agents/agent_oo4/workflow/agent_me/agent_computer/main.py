import json
from typing import List
from core.clients.llm import LLMClient
from core.clients.som import OmniparserClient
from core.models import Message, TextContent, ImageContent, ToolResult
from core.message_store import MessageStore
from core.state import State
from core.tracker import Tracker
from agent_oo4.helpers import encode_image, fm
from agent_oo4.environment.computer.env import ComputerEnv

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

        # self.llm = LLMClient("azure", model="gpt-4o", deployment="gpt-4o-deployment")
        self.llm = LLMClient("azure", model="gpt-4o-mini", deployment="gpt-4o-mini-deployment")
        # self.llm = LLMClient("openai", model="gpt-4o")
        # self.llm = LLMClient("ollama", model="llama3.2-vision:latest")
        # self.llm = LLMClient("anthropic", model="claude-3-7-sonnet-20250219")

        self.som = OmniparserClient()
        self.computerEnv = env

    async def run(self) -> List[Message]:
        logger.debug("Running ...")

        # ----------------------
        # ----------------------
        # ACTIONS LOOP
        # ----------------------
        # ----------------------
        messages_store = MessageStore()

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

        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(
            role="user", 
            content=[
                TextContent(type="text", text=USER_MESSAGE.format(
                                                    plan_step=plan_step,
                                                    ui_elements=parsed["parsed_content_list"]
                                                )),
                ImageContent(
                    type="image",        
                    data=encode_image(parsed["parsed_image"]),
                    media_type="image/png"
                )
            ]
        )

        messages_store.add_message(system_message)
        messages_store.add_message(user_message)

        # region Log + State + Tracker
        self.tracker.save(f"{self.name}-{0}", [
            ("system_message", system_message.model_dump()),
            ("user_message", user_message.model_dump()),
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
                ("messages", messages_store.get_messages_dict(optimized=True))
            ])
            # endregion

            # Call LLM
            result = self.llm.call(
                messages=messages_store.get_messages(),
                tools=TOOLS # CUSTOM TOOLS
            )

            messages_store.add_message(result)

            # region Log + State + Tracker
            cost = f"Provider: {self.llm.provider}, Model: {self.llm.model}, Total cost: {result.usage.cost}$"
            logger.debug(cost)
            logger.debug(fm(result.message.model_dump()))

            self.tracker.save(f"{self.name}-{loop_count}", [
                ("llm_response", result.message.model_dump()),
                ("cost", cost),
            ])
            # endregion

            # ------------------------------
            # Section where we got from LLM a text response
            # => custom implementation of TextMessageTermination
            # ------------------------------
            if result.finish_reason != "tool_calls":
                logger.debug("TextMessageTermination, end the loop")
                break

            # ------------------------------
            # Section where we got from LLM a list of function calls
            # => everything is ok, continue
            # ------------------------------
            actions_json = []
            for tool_call in result.message.tool_calls:
                action_json = {
                    "id": tool_call.id,
                    "action": tool_call.name,
                    "parameters": tool_call.arguments,
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
                tool_response = Message(
                    role="tool",
                    tool_result=ToolResult(
                        call_id=action["id"],
                        content=info["tool_result"]
                    )
                )
                messages_store.add_message(tool_response)

                

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

        
        # Remove the BASE64 image from the messages
        all_msgs = messages_store.get_messages_dict(optimized=True)

        # region Log + State + Tracker
        logger.debug("All messages:")
        logger.debug(all_msgs)

        self.tracker.save(self.name, [
            ("all_messages", all_msgs)
        ])
        # endregion

        return messages_store.get_messages()

        
    
