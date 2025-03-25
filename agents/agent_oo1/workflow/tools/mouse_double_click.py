from core.clients.computer import ComputerClient

def mouse_double_click():
    print("---------------------------------")
    print("Tool: mouse_double_click")

    print("Clicking mouse...")
    
    computer = ComputerClient()
    computer.execute_python_command("pyautogui.doubleClick()")
    
    print("---------------------------------")
    return "Double clicked with mouse."
