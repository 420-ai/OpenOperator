import time
from typing import Annotated
from agent.clients.computer.server_client import execute_python_command
from autogen_core.tools import FunctionTool
from datetime import datetime
import os
from agent.clients.som.omniparser import OmniparserClient
from agent.clients.computer.server_client import get_screenshot
import json
from agent.helpers import encode_image, resize_and_compress_image

som_client = OmniparserClient()

async def _analyse_ui_elements_fce():
    print("---------------------------------")
    print("Tool: analyse_ui_elements")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Timestamp: {timestamp}")
    screenshot_folder = os.path.join("screenshots", f"{timestamp}")
    # Ensure the output directory exists
    os.makedirs(screenshot_folder, exist_ok=True)

    screenshot_temp_folder = os.path.join("screenshots", "temp")
    os.makedirs(screenshot_temp_folder, exist_ok=True)

    try:
        # ---------------------------
        # Take a screenshot
        # ---------------------------
        screenshot = get_screenshot()
        print("Screenshot taken.")

        # Save the screenshot 
        screenshot_path = os.path.join(screenshot_folder, "origin.png")
        screenshot.save(screenshot_path)

        # ---------------------------
        # Analyse the screenshot via OmniParser
        # ---------------------------
        screenshot_analysis = som_client.analyze_image(screenshot)

        # Save parsed image
        parsed_image_path = os.path.join(screenshot_folder, "parsed_image.png")
        screenshot_analysis["parsed_image"].save(parsed_image_path)

        # Save parsed elements
        parsed_elements_path = os.path.join(screenshot_folder, "parsed_elements.json")
        with open(parsed_elements_path, "w", encoding="utf-8") as f:
            json.dump(screenshot_analysis["parsed_content_list"], f, ensure_ascii=False, indent=4)

        print("Image read as base64.")

        # ---------------------------
        # Analyse the screenshot via OmniParser
        # ---------------------------

        parsed_image_resized = resize_and_compress_image(screenshot_analysis["parsed_image"])

        # Save resized parsed image
        parsed_image_resized_path = os.path.join(screenshot_folder, "parsed_image_resized.png")
        parsed_image_resized.save(parsed_image_resized_path)
        parsed_image_resized.save(screenshot_temp_folder + "/parsed_image_resized.png")

        # Convert to base64
        # parsed_image_resized_base64 = encode_image(parsed_image_resized)

        print("---------------------------------")

    except Exception as e:
        print("An unexpected error occurred:", e)
        raise e


    # result = {
    #     "parsed_image_base64": parsed_image_resized_base64,
    #     "parsed_content_list": screenshot_analysis["parsed_content_list"],
    # }
    # return json.dumps(result)

    return screenshot_analysis["parsed_content_list"]



analyse_ui_elements = FunctionTool(
    _analyse_ui_elements_fce, 
    description="""
    Use this to locate UI elements on a screenshot. 
    Returns a dictionary containing the screenshot with higlighted UI elements, parsed text in UI elements, and coordinates of UI elements.
    Screenshot highlights UI elements on the picture.
    Parsed elements provide a list of UI elements on the picture.
    Parsed coordinates provide a list of coordinates for all UI elements.
    """
)