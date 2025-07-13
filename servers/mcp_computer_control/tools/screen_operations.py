import pyautogui
import base64
import io
import platform
import subprocess
import os
from PIL import Image
from typing import Optional, Dict, Any, Tuple

# Linux-specific imports
if platform.system() == 'Linux':
    try:
        from Xcursor import Xcursor
    except ImportError:
        Xcursor = None

def take_screenshot(region: Optional[Tuple[int, int, int, int]] = None, 
                   format: str = "PNG", 
                   quality: int = 95) -> Dict[str, Any]:
    """Capture current screen state and return image data."""
    try:
        if region:
            x, y, width, height = region
            screen_width, screen_height = pyautogui.size()
            
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return {
                    "success": False,
                    "error": f"Region start ({x}, {y}) is outside screen bounds ({screen_width}x{screen_height})"
                }
            
            if x + width > screen_width or y + height > screen_height:
                return {
                    "success": False,
                    "error": f"Region extends beyond screen bounds"
                }
            
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            screenshot = pyautogui.screenshot()
        
        buffer = io.BytesIO()
        save_format = format.upper()
        
        if save_format == "JPEG" or save_format == "JPG":
            screenshot.save(buffer, format="JPEG", quality=quality)
        else:
            screenshot.save(buffer, format="PNG")
        
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        screen_size = pyautogui.size()
        
        return {
            "success": True,
            "image_data": image_base64,
            "format": save_format,
            "size": {"width": screenshot.width, "height": screenshot.height},
            "screen_size": {"width": screen_size[0], "height": screen_size[1]},
            "region": region if region else None,
            "data_size_bytes": len(image_bytes)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_screen_size() -> Dict[str, Any]:
    """Get current screen resolution and information."""
    try:
        width, height = pyautogui.size()
        return {
            "success": True,
            "width": width,
            "height": height,
            "size": f"{width}x{height}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_pixel_color(x: int, y: int) -> Dict[str, Any]:
    """Get the RGB color of a pixel at specified coordinates."""
    try:
        screen_width, screen_height = pyautogui.size()
        
        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            return {
                "success": False,
                "error": f"Coordinates ({x}, {y}) are outside screen bounds ({screen_width}x{screen_height})"
            }
        
        color = pyautogui.pixel(x, y)
        
        return {
            "success": True,
            "position": {"x": x, "y": y},
            "color": {
                "r": color[0],
                "g": color[1], 
                "b": color[2]
            },
            "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def locate_image_on_screen(image_path: str, confidence: float = 0.9) -> Dict[str, Any]:
    """Locate an image on the screen and return its position."""
    try:
        import os
        if not os.path.exists(image_path):
            return {"success": False, "error": f"Image file not found: {image_path}"}
        
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        
        if location:
            center = pyautogui.center(location)
            return {
                "success": True,
                "found": True,
                "location": {
                    "left": location.left,
                    "top": location.top,
                    "width": location.width,
                    "height": location.height
                },
                "center": {"x": center.x, "y": center.y},
                "confidence": confidence
            }
        else:
            return {
                "success": True,
                "found": False,
                "confidence": confidence
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def take_screenshot_with_cursor(region: Optional[Tuple[int, int, int, int]] = None, 
                               format: str = "PNG", 
                               quality: int = 95) -> Dict[str, Any]:
    """Capture current screen state with cursor visible and return image data."""
    try:
        user_platform = platform.system()
        
        # Take a screenshot first
        if region:
            x, y, width, height = region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            screenshot = pyautogui.screenshot()
        
        # Get cursor position
        cursor_x, cursor_y = pyautogui.position()
        
        # Add cursor to screenshot based on platform
        if user_platform == "Windows":
            # Try to load cursor image
            cursor_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "cursor.png")
            if os.path.exists(cursor_path):
                cursor = Image.open(cursor_path)
                # Make cursor bigger
                cursor = cursor.resize((int(cursor.width * 2), int(cursor.height * 2)))
                # Adjust cursor position if screenshot is a region
                if region:
                    cursor_x -= region[0]
                    cursor_y -= region[1]
                # Only paste if cursor is within the screenshot bounds
                if 0 <= cursor_x < screenshot.width and 0 <= cursor_y < screenshot.height:
                    screenshot.paste(cursor, (cursor_x, cursor_y), cursor)
        
        elif user_platform == "Linux":
            if Xcursor:
                try:
                    cursor_obj = Xcursor()
                    imgarray = cursor_obj.getCursorImageArrayFast()
                    cursor_img = Image.fromarray(imgarray)
                    # Adjust cursor position if screenshot is a region
                    if region:
                        cursor_x -= region[0]
                        cursor_y -= region[1]
                    # Only paste if cursor is within the screenshot bounds
                    if 0 <= cursor_x < screenshot.width and 0 <= cursor_y < screenshot.height:
                        screenshot.paste(cursor_img, (cursor_x, cursor_y), cursor_img)
                except Exception as e:
                    # If cursor capture fails, continue without cursor
                    pass
        
        elif user_platform == "Darwin":  # macOS
            # On macOS, we can use screencapture command with -C flag
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                # Use screencapture with cursor
                if region:
                    subprocess.run([
                        "screencapture", "-C", "-x",
                        "-R", f"{region[0]},{region[1]},{region[2]},{region[3]}",
                        tmp_path
                    ])
                else:
                    subprocess.run(["screencapture", "-C", "-x", tmp_path])
                
                # Load the screenshot
                screenshot = Image.open(tmp_path)
                os.unlink(tmp_path)
            except Exception:
                # Fallback to regular screenshot without cursor
                pass
        
        # Convert to requested format
        buffer = io.BytesIO()
        save_format = format.upper()
        
        if save_format == "JPEG" or save_format == "JPG":
            screenshot.save(buffer, format="JPEG", quality=quality)
        else:
            screenshot.save(buffer, format="PNG")
        
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        screen_size = pyautogui.size()
        
        return {
            "success": True,
            "image_data": image_base64,
            "format": save_format,
            "size": {"width": screenshot.width, "height": screenshot.height},
            "screen_size": {"width": screen_size[0], "height": screen_size[1]},
            "region": region if region else None,
            "cursor_position": {"x": cursor_x, "y": cursor_y},
            "data_size_bytes": len(image_bytes)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}