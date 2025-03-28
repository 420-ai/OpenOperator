import os
import pyautogui
from PIL import Image
import subprocess
import platform
import logging
from io import BytesIO


def get_screenshot_with_cursor() -> bytes:
    user_platform = platform.system()
    buffer = BytesIO()

    if user_platform == "Windows":
        cursor_path = os.path.join(os.path.dirname(__file__), "img", "cursor.png")
        screenshot = pyautogui.screenshot()
        cursor_x, cursor_y = pyautogui.position()
        cursor = Image.open(cursor_path)
        cursor = cursor.resize((int(cursor.width * 2), int(cursor.height * 2)))
        screenshot.paste(cursor, (cursor_x, cursor_y), cursor)
        screenshot.save(buffer, format="PNG")

    elif user_platform == "Darwin":  # macOS
        temp_path = os.path.join(os.path.dirname(__file__), "screenshots", "screenshot_mac.png")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        subprocess.run(["screencapture", "-C", temp_path])
        with open(temp_path, "rb") as f:
            buffer.write(f.read())

    else:
        logging.warning(f"The platform you're using ({user_platform}) is not currently supported")
        return b""

    buffer.seek(0)
    return buffer.read()
