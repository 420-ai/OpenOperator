import time
from typing import Annotated
from clients.computer import ComputerClient

def mouse_double_click(server_url: Annotated[str, "The URL of the computer server."],):
    print("---------------------------------")
    print("Tool: mouse_double_click")

    print("Clicking mouse...")
    
    computer = ComputerClient(server_url=server_url)
    computer.execute_python_command("pyautogui.doubleClick()")
    
    print("---------------------------------")
    return "Double clicked with mouse."
