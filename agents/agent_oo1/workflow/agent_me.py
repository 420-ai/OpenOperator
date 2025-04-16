import sys
import os
from core.state import State
from core.tracker import Tracker
from core.clients.llm import LLMClient
from core.clients.som import OmniparserClient
from core.clients.computer import ComputerClient
from core.models import Message, TextContent, ImageContent, ToolResult
from core.message_store import MessageStore
from agent_oo1.helpers import encode_image, fm
from agent_oo1.helpers import resize_and_compress_image
from agent_oo1.workflow.tools.keyboard_type import keyboard_type
from agent_oo1.workflow.tools.keyboard_hotkeys import keyboard_hotkeys
from agent_oo1.workflow.tools.mouse_move import mouse_move
from agent_oo1.workflow.tools.mouse_scroll import mouse_scroll
from agent_oo1.workflow.tools.mouse_left_click import mouse_left_click
from agent_oo1.workflow.tools.mouse_double_click import mouse_double_click


import logging
logger = logging.getLogger("agent_me")


SYSTEM_MESSAGE = """
You are a helpful and intelligent AI agent working on a computer. Your job is to complete the user's task by reasoning step-by-step and using available tools (functions) only when necessary.

You can assume that Microsoft Teams is installed and is pinned in the Task Bar.

You receive a screenshot of the user's screen with each message. All visible UI elements are listed with IDs and coordinates.

Use the screenshot and UI element data to understand what is currently visible to the user.

Your workflow:
1. Think carefully about the user's instruction and your current progress.
2. If you already have enough information to complete the task, respond with "ALL DONE" and summarize the actions taken.
3. Otherwise, reason about what is missing, and call the most appropriate tool to continue.

Never call tools blindly or repeatedly. Always explain your reasoning before taking action.

Always act with the end goal in mind.
"""

USER_MESSAGE_INSTRUCTION = """
Here is the user task.
=========================
{instruction}
=========================
"""

USER_MESSAGE_SCREENSHOT = """
Attached is the current screenshot of the desktop. This screenshot shows what is currently visible to the user.

All visible UI elements in the screenshot are listed below. Each UI element has a unique ID and its screen coordinates.

Use this to understand what the user sees and reason about what to do next.
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


model = os.getenv("AZURE_MODEL", "gpt-4o")
model_deployment = os.getenv("AZURE_MODEL_DEPLOYMENT_NAME", "gpt-4o-deployment")

class OOAgentMe:
    """
    This is the main class for the OOAgentMe agent.
    It handles the initialization and execution
    of the agent's tasks.
    """

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "agent_me"
        self.description = "Agent representing a user controlling computer"

        self.state = state
        self.config = state.get_config()
        self.tracker = tracker  

        self.llm = LLMClient("azure", model=model, deployment=model_deployment)
        self.message_store = MessageStore()

        self.computer = ComputerClient()
        self.som = OmniparserClient()

        self.tools = [
            keyboard_type,
            keyboard_hotkeys,
            mouse_move,
            mouse_scroll,
            mouse_left_click,
            mouse_double_click,
        ]

    async def run(self) -> str:
        logger.debug("Running ...")

        # Log the current step
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
        logger.debug("Running...")
        self.state.create_new_plan_version()

        instruction = os.getenv("INSTRUCTION", self.config.instruction)

        print(f"Instruction envVar: {instruction}")

        if instruction == "":
            instruction = self.config.instruction

        print("final instruction: ", instruction)

        # Prepare messages for the LLM
        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(
                role="user", 
                content=USER_MESSAGE_INSTRUCTION.format(
                    instruction=instruction
                )
            )

        self.message_store.add_message(system_message)
        self.message_store.add_message(user_message)

        # region Log + State + Tracker
        logger.debug(system_message.model_dump())
        logger.debug(user_message.model_dump())

        self.state.save_plan_text(self.config.instruction)

        self.tracker.save(self.name, [
            ("instruction", self.config.instruction),
            ("system_message", system_message.model_dump()),
            ("user_message", user_message.model_dump()),
        ])
        # endregion


        planIteration = -1
        planValidation = False
        while planIteration < self.config.workflow.params.max_plan_versions:
            planIteration += 1

            logger.debug("--------------------------")
            logger.debug(f"Agent - Plan version: {planIteration}")
            logger.debug("--------------------------")
            if planIteration > 0:
                # Create a new plan version
                logger.debug("Creating new plan version")
                self.state.create_new_plan_version()

            # region Log + State + Tracker
            self.tracker.save(f"{self.name}-{planIteration}", [
                ("messages", self.message_store.get_messages_dict(optimized=True))
            ])
            # endregion

            # ----------------------
            # Capture state before actions
            # ----------------------
            # Take a screenshot
            screenshot_t0 = self.computer.get_screenshot()
            screenshot_t0_resized = resize_and_compress_image(screenshot_t0)

            # Analyze the screenshot and get the UI elements
            parsed_t0 = self.som.analyze_image(screenshot_t0)

            # Prepare messages for the LLM
            user_message = Message(
                role="user", 
                content=[
                    TextContent(type="text", text=USER_MESSAGE_SCREENSHOT.format(
                                                        ui_elements=parsed_t0["parsed_content_list"]
                                                    )),
                    ImageContent(
                        type="image",        
                        data=encode_image(parsed_t0["parsed_image"]),
                        media_type="image/png"
                    )
                ]
            )

            self.message_store.add_message(user_message)

            # region Log + State + Tracker
            self.state.save_plan_image(screenshot_t0_resized, "t0_resized.png")
            self.state.save_plan_image(parsed_t0["parsed_image"], "t0_parsed.png")

            self.tracker.save(f"{self.name}-{planIteration}", [
                ("user_message", user_message.model_dump()),
                ("screenshot_t0_resized", screenshot_t0_resized),
                ("screenshot_t0_parsed", parsed_t0["parsed_image"]),
                ("parsed_content_list", parsed_t0["parsed_content_list"]),
            ])
            # endregion


            # ----------------------
            # ----------------------
            # Call LLM
            # ----------------------
            # ----------------------

            # Call the LLM
            llm_result = self.llm.call(
                messages=self.message_store.get_messages(),
                tools=TOOLS,
            )

            # Add message to the message store
            self.message_store.add_message(llm_result)

            # region Log + State + Tracker
            cost = f"Provider: {self.llm.provider}, Model: {self.llm.model}, Total cost: {llm_result.usage.cost}$"
            logger.debug(cost)
            logger.debug(fm(llm_result.message.model_dump()))

            self.tracker.save(f"{self.name}-{planIteration}", [
                ("llm_response", llm_result.message.model_dump()),
                ("cost", cost),
            ])
            # endregion


            # ----------------------
            # ----------------------
            # Should we continue?
            # ----------------------
            # ----------------------

            # "ALL DONE"
            if "ALL DONE" in llm_result.message.content:
                planValidation = True
                logger.debug("Plan is done")
                break


            # Text response
            if llm_result.finish_reason != "tool_calls":
                logger.debug("TextMessageTermination, end the loop")
                break

            # ----------------------
            # ----------------------
            # Tool calls
            # ----------------------
            # ----------------------
            for tool_call in llm_result.message.tool_calls:
                tool_call_id = tool_call.id
                tool_name = tool_call.name
                tool_arguments = tool_call.arguments

                # 1. Find the tool in the list
                tool_selected = next((t for t in self.tools if t.__name__ == tool_name), None)
                if not tool_selected:
                    raise ValueError(f"Invalid action type: {tool_name}")
                
                # 2. Execute the tool
                tool_result = tool_selected(**tool_arguments)

                # Add the tool result to the message store
                tool_response = Message(
                    role="tool",
                    tool_result=ToolResult(
                        call_id=tool_call_id,
                        content=tool_result
                    )
                )
                self.message_store.add_message(tool_response)


        # Save the plan step result to the state
        if planValidation == True:
            plan_result = f"Plan is successfuly done after {str(planIteration)} iterations."
        elif planValidation == False and planIteration < self.config.workflow.params.max_plan_versions:
            plan_result = f"Plan is not done after {str(planIteration)} iterations. We got a text response from the LLM, but not 'ALL DONE'."
        else:
            # Add a summarization of the all actions taken for this plan step
            plan_result = f"Plan reached max iterations of {str(self.config.workflow.params.max_plan_versions)}."

        # region Log + State + Tracker
        logger.debug(plan_result)

        self.state.save_plan_result(plan_result)

        self.tracker.save(self.name, [
            ("plan_result", plan_result),
        ])
        # endregion

        # ----------------------------------------
        # Perhaps not needed to return any string
        return plan_result