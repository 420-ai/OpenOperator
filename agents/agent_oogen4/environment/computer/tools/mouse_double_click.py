import time
from typing import Annotated
from clients.computer import computer

def mouse_double_click():
    print("---------------------------------")
    print("Tool: mouse_double_click")

    print("Clicking mouse...")
    
    computer.execute_python_command("pyautogui.doubleClick()")
    
    print("---------------------------------")
    return "Double clicked with mouse."
