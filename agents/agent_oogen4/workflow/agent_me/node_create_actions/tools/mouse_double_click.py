import time
from typing import Annotated
from autogen_core.tools import FunctionTool
from clients.computer import computer

async def _mouse_double_click_fce():
    print("---------------------------------")
    print("Tool: mouse_double_click")

    print("Clicking mouse...")
    
    computer.execute_python_command("pyautogui.doubleClick()")
    
    print("---------------------------------")
    return "Double clicked with mouse."


mouse_double_click = FunctionTool(
    _mouse_double_click_fce, 
    name="mouse_double_click",
    description="Double click with mouse."
)