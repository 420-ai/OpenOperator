
import time
from typing import Annotated
from autogen_core.tools import FunctionTool
from clients.computer import computer

async def _keyboard_type_fce(
    text: Annotated[str, "The text to type on keyboard."],
):
    print("---------------------------------")
    print("Tool: keyboard_type")
    print(f"Text: {text}")

    print("Typing text...")
    time.sleep(1)
    
    computer.execute_python_command("pyautogui.typewrite({:})".format(repr(text)))
    print("---------------------------------")
    return f"Typed text: {text}"


keyboard_type = FunctionTool(
    _keyboard_type_fce, 
    name="keyboard_type",
    description="Type text with keyboard."
)