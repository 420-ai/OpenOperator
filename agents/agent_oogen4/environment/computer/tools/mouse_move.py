
import time
from typing import Annotated
from clients.computer import ComputerClient

def mouse_move(
    x: Annotated[int, "The x coordinate (absolute) to move to."],
    y: Annotated[int, "The y coordinate (absolute) to move to."],
    server_url: Annotated[str, "The URL of the computer server."],
):
    print("---------------------------------")
    print(f"Tool: mouse_move")
    print(f"x: {x}, y: {y}")

    print("Moving mouse...")

    duration = 0.5

    computer = ComputerClient(server_url=server_url)
    computer.execute_python_command(f"pyautogui.moveTo({x}, {y}, {duration})")
    
    print("---------------------------------")
    return f"Moved mouse to x: {x}, y: {y}"
