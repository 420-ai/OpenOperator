
import time
from typing import Annotated
from workflow.clients.computer import ComputerClient
from autogen_core.tools import FunctionTool
from config import config

async def _mouse_move_fce(
    x: Annotated[int, "The x coordinate (absolute) to move to."],
    y: Annotated[int, "The y coordinate (absolute) to move to."],
):
    # print("---------------------------------")
    # print(f"Tool: mouse_move")
    # print(f"x: {x}, y: {y}")

    # print("Moving mouse...")

    duration = 0.5

    server_url=f"{config.environment.params.server_ip}:{config.environment.params.computer_port}"
    computer = ComputerClient(server_url=server_url)
    computer.execute_python_command(f"pyautogui.moveTo({x}, {y}, {duration})")
    
    # print("---------------------------------")
    return f"Moved mouse to x: {x}, y: {y}"


mouse_move = FunctionTool(
    _mouse_move_fce, 
    description="Move the mouse to a specific location. Coordinates are absolute with respect to the screen resolution."
)