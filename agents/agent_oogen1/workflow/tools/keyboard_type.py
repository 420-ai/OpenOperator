
import time
from typing import Annotated
from workflow.clients.computer import ComputerClient
from autogen_core.tools import FunctionTool
from config import config

async def _keyboard_type_fce(
    text: Annotated[str, "The text to type on keyboard."],
):
    # print("---------------------------------")
    # print("Tool: keyboard_type")
    # print(f"Text: {text}")

    # print("Typing text...")
    time.sleep(1)
    
    server_url=f"{config.environment.params.server_ip}:{config.environment.params.computer_port}"
    computer = ComputerClient(server_url=server_url)
    computer.execute_python_command("pyautogui.typewrite({:})".format(repr(text)))
    # print("---------------------------------")
    return f"Typed text: {text}"


keyboard_type = FunctionTool(
    _keyboard_type_fce, 
    description="Type text with keyboard."
)