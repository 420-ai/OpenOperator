from utils.execute_python_command import execute_python_command

def mouse_left_click():
    print("---------------------------------")
    print("Tool: mouse_left_click")

    print("Clicking mouse...")
    
    execute_python_command("pyautogui.click()")
    
    print("---------------------------------")
    return "Left clicked with mouse."
