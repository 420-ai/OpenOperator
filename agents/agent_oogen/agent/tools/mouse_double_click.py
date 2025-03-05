import time
from typing import Annotated
from agent.clients.computer.server_client import execute_python_command
from autogen_core.tools import FunctionTool

async def _mouse_double_click_fce():
    print("---------------------------------")
    print("Tool: mouse_double_click")

    print("Clicking mouse...")
    
    execute_python_command("pyautogui.doubleClick()")
    
    print("---------------------------------")


mouse_double_click = FunctionTool(
    _mouse_double_click_fce, 
    description="Double click with mouse."
)