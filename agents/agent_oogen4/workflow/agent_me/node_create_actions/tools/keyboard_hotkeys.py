
import time
from typing import Annotated
from autogen_core.tools import FunctionTool
from clients.computer import computer

async def _keyboard_hotkeys_fce(
   hotkeys: Annotated[list, "List of hotkeys to press (e.g., ['cmd', 'a'])"],
):
    print("---------------------------------")
    print("Tool: keyboard_hotkey")
    print(f"Hotkeys: {hotkeys}")

    print("Pressing hotkeys...")

    keys_para_rep = "', '".join(hotkeys)
    
    computer.execute_python_command(f"pyautogui.hotkey('{keys_para_rep}')")
    print("---------------------------------")
    return f"Pressed hotkeys: {hotkeys}"


keyboard_hotkeys = FunctionTool(
    _keyboard_hotkeys_fce, 
    name="keyboard_hotkeys",
    description="Simulates pressing a sequence of hotkeys"
)