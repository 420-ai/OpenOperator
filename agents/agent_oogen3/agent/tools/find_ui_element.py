import time
import traceback
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

som_client = OmniparserClient()

SYSTEM_MESSAGE = "You are an AI assistant responsible for finding UI elements in a screenshot."
USER_MESSAGE = """
Find the UI element in the screenshot and return its ID.
If you cannot find the UI element return -1.

Find UI element based on this description:
{objective}

Output format:
ID=1
"""

async def _find_ui_element_fce(
    ui_element: Annotated[str, "The description of the UI element to find"],
):
    print("---------------------------------")
    print("Tool: find_ui_element")

    try:
        # Take a screenshot
        screenshot = get_screenshot()

        # Resize and compress the screenshot
        # screenshot_resized = resize_and_compress_image(screenshot)

        # Analyse the screenshot
        screenshot_analysis = som_client.analyze_image(screenshot)

        # ---------------------------
        # Ask LLM to find the UI element
        # ---------------------------
        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        user_message = UserMessage(content=[
            USER_MESSAGE.format(objective=ui_element), 
            AutogenImage.from_pil(screenshot_analysis["parsed_image"])
        ], source="user")

        llm_response = await llm.create(messages=[
            system_message,
            user_message,
        ])

        print("LLM response:", llm_response.content)  

        found_id = llm_response.content.split("=")[1].strip()
        print("Found ID:", found_id)

        searched_ui_element = None 
        
        for elem in screenshot_analysis["parsed_content_list"]:
            if str(elem["id"]) == found_id:
                searched_ui_element = elem
                break

        print("Searched UI element:", searched_ui_element)
        print("---------------------------------")
        return searched_ui_element

    except Exception as e:
        print("An unexpected error occurred:", e)
        error_traceback = traceback.format_exc()
        print(error_traceback)
        raise e




find_ui_element = FunctionTool(
    _find_ui_element_fce, 
    description="""
Use this to locate UI element on a screenshot. 
Returns a coordinates of the element if exist.
Example:
{
    "id": 26,
    "from": "omniparser",
    "type": "icon",
    "text": "Notepad ",
    "shape": {
        "x": 1534,
        "y": 1083,
        "width": 192,
        "height": 138
    },
    "click": {
        "x": 1630,
        "y": 1153
    },
    "interactivity": true
},
"""
)