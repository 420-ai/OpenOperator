from core.clients.computer import ComputerClient

def mouse_left_click():
    print("---------------------------------")
    print("Tool: mouse_left_click")

    print("Clicking mouse...")
    
    computer = ComputerClient()
    computer.execute_python_command("pyautogui.click()")
    
    print("---------------------------------")
    return "Left clicked with mouse."
