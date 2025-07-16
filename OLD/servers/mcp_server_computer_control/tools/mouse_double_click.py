from utils.execute_python_command import execute_python_command

def mouse_double_click():
    print("---------------------------------")
    print("Tool: mouse_double_click")

    print("Clicking mouse...")
    
    execute_python_command("pyautogui.doubleClick()")
    
    print("---------------------------------")
    return "Double clicked with mouse."
