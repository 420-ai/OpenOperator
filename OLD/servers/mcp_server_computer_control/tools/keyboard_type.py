import time
from typing import Annotated
from utils.execute_python_command import execute_python_command

def keyboard_type(
    text: Annotated[str, "The text to type on keyboard."],
):
    print("---------------------------------")
    print("Tool: keyboard_type")
    print(f"Text: {text}")

    print("Typing text...")
    time.sleep(1)
    
    execute_python_command("pyautogui.typewrite({:})".format(repr(text)))
    print("---------------------------------")
    return f"Typed text: {text}"
