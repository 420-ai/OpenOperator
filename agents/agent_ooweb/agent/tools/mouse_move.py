
import time
from typing import Annotated
from agent.clients.computer.server_client import execute_python_command
from autogen_core.tools import FunctionTool

async def _mouse_move_fce(
    x: Annotated[int, "The x coordinate (absolute) to move to."],
    y: Annotated[int, "The y coordinate (absolute) to move to."],
):
    print("---------------------------------")
    print(f"Tool: mouse_move")
    print(f"x: {x}, y: {y}")

    print("Moving mouse...")

    duration = 0.5
    execute_python_command(f"pyautogui.moveTo({x}, {y}, {duration})")
    
    print("---------------------------------")


mouse_move = FunctionTool(
    _mouse_move_fce, 
    description="Move the mouse to a specific location. Coordinates are absolute with respect to the screen resolution."
)