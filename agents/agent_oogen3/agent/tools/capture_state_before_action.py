from autogen_core.tools import FunctionTool
from agent.clients.som.omniparser import OmniparserClient
from agent.clients.computer.server_client import get_screenshot
from agent.helpers import resize_and_compress_image

som_client = OmniparserClient()

async def _capture_state_before_action_fce():
    print("---------------------------------")
    print("Tool: capture_state_before_action")

    try:
        # Take a screenshot
        screenshot = get_screenshot()

        # Resize and compress the screenshot
        screenshot_resized = resize_and_compress_image(screenshot)

        screenshot_resized.save("screenshot_before_action.png")
        
        print("---------------------------------")
        return "Screenshot captured successfully."

    except Exception as e:
        print("An unexpected error occurred:", e)
        raise e

capture_state_before_action = FunctionTool(
    _capture_state_before_action_fce, 
    description="""Use this to take a screenshot of the current state of the UI. Usually used before an action is performed."""
)