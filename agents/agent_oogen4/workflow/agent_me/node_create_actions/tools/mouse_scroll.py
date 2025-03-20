
import time
from typing import Annotated
from autogen_core.tools import FunctionTool
from clients.computer import computer

async def _mouse_scroll_fce(
    direction: Annotated[str, "'up', 'down', 'left', 'right. Determines the direction of scrolling."],
    amount: Annotated[int, "The scroll amount. Positive values move in the natural direction."],
    delay: Annotated[float, "Delay (in seconds) between consecutive scrolls. Default is 0."],
    steps: Annotated[int, "Number of times to apply the scroll for smoother motion."],
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
    
    for _ in range(steps):
        computer.execute_python_command(scroll_func[direction]())
        time.sleep(delay)

    return f"Scrolled {amount} in the {direction} direction."


mouse_scroll = FunctionTool(
    _mouse_scroll_fce, 
    name="mouse_scroll", 
    description="Performs a scrolling action in the specified direction ('up', 'down', 'left', or 'right'). "
                "Use this tool whenever scrolling is needed to navigate through content that is not fully visible on the screen. "
                "The scroll amount controls the intensity, and steps allow for smooth scrolling."
)