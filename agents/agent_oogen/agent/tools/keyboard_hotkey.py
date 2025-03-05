
import time
from typing import Annotated
from agent.clients.computer.server_client import execute_python_command
from autogen_core.tools import FunctionTool

async def _keyboard_hotkeys_fce(
   hotkeys: Annotated[list, "List of hotkeys to press (e.g., ['cmd', 'a'])"],
):
    print("---------------------------------")
    print("Tool: keyboard_hotkey")
    print(f"Hotkeys: {hotkeys}")

    print("Pressing hotkeys...")

    keys_para_rep = "', '".join(hotkeys)
    
    execute_python_command(f"pyautogui.hotkey('{keys_para_rep}')")
    print("---------------------------------")


keyboard_hotkeys = FunctionTool(
    _keyboard_hotkeys_fce, 
    description="Simulates pressing a sequence of hotkeys"
)