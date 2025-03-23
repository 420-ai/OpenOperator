
import time
from typing import Annotated
from workflow.clients.computer import ComputerClient
from autogen_core.tools import FunctionTool
from config import config

async def _keyboard_hotkeys_fce(
   hotkeys: Annotated[list, "List of hotkeys to press (e.g., ['cmd', 'a'])"],
):
    # print("---------------------------------")
    # print("Tool: keyboard_hotkey")
    # print(f"Hotkeys: {hotkeys}")

    # print("Pressing hotkeys...")

    keys_para_rep = "', '".join(hotkeys)
    
    server_url=f"{config.environment.params.server_ip}:{config.environment.params.computer_port}"
    computer = ComputerClient(server_url=server_url)
    computer.execute_python_command(f"pyautogui.hotkey('{keys_para_rep}')")
    # print("---------------------------------")
    return f"Pressed hotkeys: {hotkeys}"


keyboard_hotkeys = FunctionTool(
    _keyboard_hotkeys_fce, 
    description="Simulates pressing a sequence of hotkeys"
)