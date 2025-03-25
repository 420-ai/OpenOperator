import time
from typing import Annotated
from core.clients.computer import ComputerClient

def keyboard_type(
    text: Annotated[str, "The text to type on keyboard."],
):
    print("---------------------------------")
    print("Tool: keyboard_type")
    print(f"Text: {text}")

    print("Typing text...")
    time.sleep(1)
    
    computer = ComputerClient()
    computer.execute_python_command("pyautogui.typewrite({:})".format(repr(text)))
    print("---------------------------------")
    return f"Typed text: {text}"
