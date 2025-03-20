
import time
from typing import Annotated
from clients.computer import ComputerClient

def keyboard_type(
    text: Annotated[str, "The text to type on keyboard."],
    server_url: Annotated[str, "The URL of the computer server."],
):
    print("---------------------------------")
    print("Tool: keyboard_type")
    print(f"Text: {text}")

    print("Typing text...")
    time.sleep(1)
    
    computer = ComputerClient(server_url=server_url)
    computer.execute_python_command("pyautogui.typewrite({:})".format(repr(text)))
    print("---------------------------------")
    return f"Typed text: {text}"
