from typing import Annotated
from core.clients.computer import ComputerClient

def keyboard_hotkeys(
   hotkeys: Annotated[list, "List of hotkeys to press (e.g., ['cmd', 'a'])"]
):
    print("---------------------------------")
    print("Tool: keyboard_hotkey")
    print(f"Hotkeys: {hotkeys}")

    print("Pressing hotkeys...")

    keys_para_rep = "', '".join(hotkeys)
    
    computer = ComputerClient()
    computer.execute_python_command(f"pyautogui.hotkey('{keys_para_rep}')")
    print("---------------------------------")
    return f"Pressed hotkeys: {hotkeys}"
