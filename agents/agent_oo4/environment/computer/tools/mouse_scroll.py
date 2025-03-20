
import time
from typing import Annotated
from clients.computer import ComputerClient

def mouse_scroll(
    direction: Annotated[str, "'up', 'down', 'left', 'right. Determines the direction of scrolling."],
    amount: Annotated[int, "The scroll amount. Positive values move in the natural direction."],
    delay: Annotated[float, "Delay (in seconds) between consecutive scrolls. Default is 0."],
    steps: Annotated[int, "Number of times to apply the scroll for smoother motion."],
    server_url: Annotated[str, "The URL of the computer server."],
):
    direction = direction.lower()
    if direction not in ["up", "down", "left", "right"]:
        raise ValueError("Invalid direction. Use 'up', 'down', 'left', or 'right'.")
    
    scroll_func = {
        "up": lambda: f"pyautogui.vscroll({amount})",
        "down": lambda: f"pyautogui.vscroll({-amount})",
        "left": lambda: f"pyautogui.hscroll({-amount})",
        "right": lambda: f"pyautogui.hscroll({amount})",
    }
    
    computer = ComputerClient(server_url=server_url)
    for _ in range(steps):
        computer.execute_python_command(scroll_func[direction]())
        time.sleep(delay)

    return f"Scrolled {amount} in the {direction} direction."
