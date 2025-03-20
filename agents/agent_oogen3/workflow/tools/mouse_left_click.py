import time
from typing import Annotated
from workflow.clients.computer import ComputerClient
from autogen_core.tools import FunctionTool
from config import config

async def _mouse_left_click_fce():
    # print("---------------------------------")
    # print("Tool: mouse_left_click")

    # print("Clicking mouse...")
    
    server_url=f"{config.environment.params.server_ip}:{config.environment.params.computer_port}"
    computer = ComputerClient(server_url=server_url)
    computer.execute_python_command("pyautogui.click()")
    
    # print("---------------------------------")
    return "Left clicked with mouse."


mouse_left_click = FunctionTool(
    _mouse_left_click_fce, 
    description="Left click with mouse."
)