import time
from typing import Annotated
from clients.computer import computer

def mouse_left_click():
    print("---------------------------------")
    print("Tool: mouse_left_click")

    print("Clicking mouse...")
    
    computer.execute_python_command("pyautogui.click()")
    
    print("---------------------------------")
    return "Left clicked with mouse."
