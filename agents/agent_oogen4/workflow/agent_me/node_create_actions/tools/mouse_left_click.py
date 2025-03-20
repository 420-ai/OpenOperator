import time
from typing import Annotated
from autogen_core.tools import FunctionTool
from clients.computer import computer

async def _mouse_left_click_fce():
    print("---------------------------------")
    print("Tool: mouse_left_click")

    print("Clicking mouse...")
    
    computer.execute_python_command("pyautogui.click()")
    
    print("---------------------------------")
    return "Left clicked with mouse."


mouse_left_click = FunctionTool(
    _mouse_left_click_fce,
    name="mouse_left_click", 
    description="Left click with mouse."
)