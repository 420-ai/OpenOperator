import pyautogui
import time
from typing import Optional, Tuple, Dict, Any

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

def mouse_move(x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
    """Move mouse cursor to specified coordinates."""
    try:
        screen_width, screen_height = pyautogui.size()
        
        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            return {
                "success": False,
                "error": f"Coordinates ({x}, {y}) are outside screen bounds ({screen_width}x{screen_height})"
            }
        
        pyautogui.moveTo(x, y, duration=duration)
        return {
            "success": True,
            "position": {"x": x, "y": y},
            "screen_size": {"width": screen_width, "height": screen_height}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def mouse_scroll(direction: str, clicks: int = 3, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
    """Scroll at current position or specified coordinates."""
    try:
        if x is not None and y is not None:
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return {
                    "success": False,
                    "error": f"Coordinates ({x}, {y}) are outside screen bounds ({screen_width}x{screen_height})"
                }
            pyautogui.moveTo(x, y)
        
        scroll_amount = clicks if direction.lower() in ["up", "vertical_up"] else -clicks
        if direction.lower() in ["left", "horizontal_left"]:
            pyautogui.hscroll(-clicks)
        elif direction.lower() in ["right", "horizontal_right"]:
            pyautogui.hscroll(clicks)
        else:
            pyautogui.scroll(scroll_amount)
        
        current_pos = pyautogui.position()
        return {
            "success": True,
            "direction": direction,
            "clicks": clicks,
            "position": {"x": current_pos.x, "y": current_pos.y}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def mouse_left_click(x: Optional[int] = None, y: Optional[int] = None, button: str = "left") -> Dict[str, Any]:
    """Perform mouse click at current position or specified coordinates."""
    try:
        if x is not None and y is not None:
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return {
                    "success": False,
                    "error": f"Coordinates ({x}, {y}) are outside screen bounds ({screen_width}x{screen_height})"
                }
            pyautogui.click(x, y, button=button)
            position = {"x": x, "y": y}
        else:
            pyautogui.click(button=button)
            current_pos = pyautogui.position()
            position = {"x": current_pos.x, "y": current_pos.y}
        
        return {
            "success": True,
            "button": button,
            "position": position
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def mouse_double_click(x: Optional[int] = None, y: Optional[int] = None, button: str = "left") -> Dict[str, Any]:
    """Perform double-click at current position or specified coordinates."""
    try:
        if x is not None and y is not None:
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return {
                    "success": False,
                    "error": f"Coordinates ({x}, {y}) are outside screen bounds ({screen_width}x{screen_height})"
                }
            pyautogui.doubleClick(x, y, button=button)
            position = {"x": x, "y": y}
        else:
            pyautogui.doubleClick(button=button)
            current_pos = pyautogui.position()
            position = {"x": current_pos.x, "y": current_pos.y}
        
        return {
            "success": True,
            "button": button,
            "position": position,
            "action": "double_click"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def mouse_right_click(x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
    """Perform right-click at current position or specified coordinates."""
    return mouse_left_click(x, y, button="right")

def mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0, button: str = "left") -> Dict[str, Any]:
    """Drag mouse from start position to end position."""
    try:
        screen_width, screen_height = pyautogui.size()
        
        if not (0 <= start_x <= screen_width and 0 <= start_y <= screen_height):
            return {
                "success": False,
                "error": f"Start coordinates ({start_x}, {start_y}) are outside screen bounds ({screen_width}x{screen_height})"
            }
        
        if not (0 <= end_x <= screen_width and 0 <= end_y <= screen_height):
            return {
                "success": False,
                "error": f"End coordinates ({end_x}, {end_y}) are outside screen bounds ({screen_width}x{screen_height})"
            }
        
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, button=button)
        
        return {
            "success": True,
            "start_position": {"x": start_x, "y": start_y},
            "end_position": {"x": end_x, "y": end_y},
            "button": button,
            "duration": duration
        }
    except Exception as e:
        return {"success": False, "error": str(e)}