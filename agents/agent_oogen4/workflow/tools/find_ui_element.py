import traceback
from typing import Annotated
from autogen_core.tools import FunctionTool
from workflow.clients.som.omniparser import OmniparserClient
from workflow.clients.computer.server_client import get_screenshot
from workflow.clients.llm.azure_openai import llm_gpt4o
from autogen_core.models import UserMessage, SystemMessage
from autogen_core import Image as AutogenImage
from workflow.tools.helpers import save_image, save_json, save_txt, save_system_message, save_user_message
import os

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
    ui_element: Annotated[str, "The description of the UI element to find on the screen"],
):
    print("---------------------------------")
    print("Tool: find_ui_element")
    print(ui_element)

    # current_dir = os.path.dirname(__file__)

    try:
        # Take a screenshot
        screenshot = get_screenshot()
        # save_image(screenshot, current_dir, "find_ui-screenshot.png")

        # Analyse the screenshot
        screenshot_analysis = som_client.analyze_image(screenshot)
        # save_image(screenshot_analysis["parsed_image"], current_dir, "find_ui-screenshot-parsed.png")
        # save_json(screenshot_analysis["parsed_content_list"], current_dir, "find_ui-screenshot-parsed.json")

        # ---------------------------
        # Ask LLM to find the UI element
        # ---------------------------
        system_message = SystemMessage(content=SYSTEM_MESSAGE)
        # save_system_message(system_message, current_dir)

        user_message = UserMessage(content=[
            USER_MESSAGE.format(objective=ui_element), 
            AutogenImage.from_pil(screenshot_analysis["parsed_image"])
        ], source="user")
        # save_user_message(user_message, current_dir)

        llm_response = await llm_gpt4o.create(messages=[
            system_message,
            user_message,
        ])

        found_id = llm_response.content.split("=")[1].strip()

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
"""
)