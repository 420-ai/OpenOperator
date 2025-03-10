from typing import Annotated
from agent.clients.computer.server_client import execute_python_command
from autogen_core.tools import FunctionTool
from datetime import datetime
import os
from agent.clients.som.omniparser import OmniparserClient
from agent.clients.computer.server_client import get_screenshot
import json
from agent.helpers import encode_image, resize_and_compress_image
from agent.clients.llm.azure_openai import llm
from autogen_core.models import UserMessage, SystemMessage
from autogen_core import Image as AutogenImage
from PIL import Image

som_client = OmniparserClient()

SYSTEM_MESSAGE = """You are an AI assistant tasked with validating whether a specific objective has been achieved. You will be provided with a detailed plan, a clearly defined objective, and one or more screenshots as evidence. Your role is to analyze the provided information and determine if the objective has been satisfied. 
You don't need to analyze the entire screenshot; focus on the specific elements relevant to the objective. Your response should include a binary conclusion (True or False) and a concise explanation based on the visible evidence in the screenshot(s).

**Guidelines for Validation:**
1. **When a single screenshot is provided:**
   - Focus exclusively on the objective and the visible evidence within the screenshot.
   - Evaluate whether the state or action described in the objective is clearly demonstrated.
   - Example: If the objective is to "click on the message input," confirm that the screenshot shows the input box clicked, selected, or focused.

2. **When two screenshots are provided:**
   - The **first screenshot** represents the state before the action, and the **second screenshot** represents the state after the action.
   - Compare the two images to identify evidence of progression, change, or completion of the described action.
   - Example 1: If the objective is to "select text in an input box," confirm that the second screenshot shows the input box with text selected that was present in the first screenshot.
   - Example 2: If the objective is to "drag and drop an item," verify that the item has moved from its initial position in the first screenshot to its intended target position in the second screenshot.

3. **General and unclear objectives:**
   - Use the plan provided as a contextual guide to interpret the objective and analyze the screenshots effectively.
   - If the screenshots or the objective do not provide sufficient evidence to reach a conclusion, explicitly state this and explain why.

**Response Requirements:**
- Always include a binary conclusion: `True` (objective satisfied) or `False` (objective not satisfied).
- Provide a concise, specific explanation for your conclusion. For example:
  - "True: The text input is selected in the second screenshot, as indicated by the visible underline."
  - "False: The input box is not selected, and no evidence of focus or selection is visible."
- Avoid assumptions not supported by the evidence in the screenshots or the plan.

Consistency, precision, and focus on the objective are essential in your analysis. Use all provided details to make an accurate and justified decision.
"""

USER_MESSAGE = """
Here is the objective:
{objective}

Please analyze the provided screenshot(s) and determine if the objective is satisfied based on the following:

1. **For one screenshot:**  
Focus on the visible evidence and its alignment with the objective.  

2. **For two screenshots:**  
The first screenshot represents the state **before** the action, and the second screenshot represents the state **after** the action.  
Compare the images to validate progression, changes, or actions that satisfy the objective. Focus only on the part of the screenshots relevant to the objective. 

Examples:  
- If the objective is "Select text in input box," verify whether the second screenshot shows the input box with the text selected that was present in the first screenshot.  
- If the objective is "Drag and drop item," confirm whether the item has moved from its source position to the target location.

Your response must include:
- A conclusion (`True` or `False`), explicitly stating whether the objective is satisfied.
- A brief explanation detailing the specific evidence from the screenshot(s) that supports your conclusion.

If the objective or evidence is unclear, rely on the plan for additional context and explain why the objective cannot be validated if applicable.
"""

async def _validate_objective_via_screenshot_fce(
    objective: Annotated[str, "The objective that needs to be validated"],
):
    print("---------------------------------")
    print("Tool: validate_objective_via_screenshot")

    try:

        # Check if screenshot_before_action.png exists
        screenshot_before_action = None
        if os.path.exists("screenshot_before_action.png"):
            # If exist load it
            screenshot_before_action = Image.open("screenshot_before_action.png")
            # and remove it
            os.remove("screenshot_before_action.png")

        # Take a screenshot
        current_screenshot = get_screenshot()

        # Resize and compress the screenshot
        current_screenshot_resized = resize_and_compress_image(current_screenshot)

        # ---------------------------
        # Ask LLM to find the UI element
        # ---------------------------
        system_message = SystemMessage(content=SYSTEM_MESSAGE)

        final_messages = [
            USER_MESSAGE.format(objective=objective)
        ]
        if screenshot_before_action is not None:
            # Add the parsed UI elements and image to the final messages
            final_messages.append("Here is the screenshot before the action:")
            final_messages.append(AutogenImage.from_pil(screenshot_before_action))
        
        final_messages.append(AutogenImage.from_pil(current_screenshot_resized))
        
        user_message = UserMessage(content=final_messages, source="user")

        llm_response = await llm.create(messages=[
            system_message,
            user_message,
        ])

        print("LLM response:", llm_response.content)    

        print("---------------------------------")
        return llm_response.content

    except Exception as e:
        print("An unexpected error occurred:", e)
        raise e




validate_objective_via_screenshot = FunctionTool(
    _validate_objective_via_screenshot_fce, 
    description="""This tool is designed to validate whether a given objective has been successfully achieved by analyzing one or more screenshots in the context of a task plan. It is specifically used when the success of an objective can be confirmed visually by examining screenshots."""
)