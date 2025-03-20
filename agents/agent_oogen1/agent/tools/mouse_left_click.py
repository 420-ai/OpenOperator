import time
from typing import Annotated
from agent.clients.computer.server_client import execute_python_command
from autogen_core.tools import FunctionTool

async def _mouse_left_click_fce():
    # print("---------------------------------")
    # print("Tool: mouse_left_click")

    # print("Clicking mouse...")
    
    execute_python_command("pyautogui.click()")
    
    # print("---------------------------------")
    return "Left clicked with mouse."


mouse_left_click = FunctionTool(
    _mouse_left_click_fce, 
    description="Left click with mouse."
)