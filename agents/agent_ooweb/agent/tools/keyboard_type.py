
import time
from typing import Annotated
from agent.clients.computer.server_client import execute_python_command
from autogen_core.tools import FunctionTool

async def _keyboard_type_fce(
    text: Annotated[str, "The text to type on keyboard."],
):
    print("---------------------------------")
    print("Tool: keyboard_type")
    print(f"Text: {text}")

    print("Typing text...")
    time.sleep(3)
    
    execute_python_command("pyautogui.typewrite({:})".format(repr(text)))
    print("---------------------------------")


keyboard_type = FunctionTool(
    _keyboard_type_fce, 
    description="Type text with keyboard."
)