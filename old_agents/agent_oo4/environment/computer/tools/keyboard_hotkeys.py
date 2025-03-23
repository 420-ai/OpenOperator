
import time
from typing import Annotated
from clients.computer import ComputerClient



def keyboard_hotkeys(
   hotkeys: Annotated[list, "List of hotkeys to press (e.g., ['cmd', 'a'])"],
   server_url: Annotated[str, "The URL of the computer server."],
):
    print("---------------------------------")
    print("Tool: keyboard_hotkey")
    print(f"Hotkeys: {hotkeys}")

    print("Pressing hotkeys...")

    keys_para_rep = "', '".join(hotkeys)
    
    computer = ComputerClient(server_url=server_url)
    computer.execute_python_command(f"pyautogui.hotkey('{keys_para_rep}')")
    print("---------------------------------")
    return f"Pressed hotkeys: {hotkeys}"
