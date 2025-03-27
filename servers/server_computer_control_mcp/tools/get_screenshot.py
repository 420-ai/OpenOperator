import os
import pyautogui
from PIL import Image
import subprocess
import platform
import logging


def get_screenshot_with_cursor():

    file_path = os.path.join(os.path.dirname(__file__), "screenshots", "screenshot.png")
    user_platform = platform.system()

    # Ensure the screenshots directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # fixme: This is a temporary fix for the cursor not being captured on Windows and Linux
    if user_platform == "Windows":
        cursor_path = os.path.join(os.path.dirname(__file__), "img", "cursor.png")
        screenshot = pyautogui.screenshot()
        cursor_x, cursor_y = pyautogui.position()
        cursor = Image.open(cursor_path)
        # make the cursor bigger
        cursor = cursor.resize((int(cursor.width * 2), int(cursor.height * 2)))
        screenshot.paste(cursor, (cursor_x, cursor_y), cursor)
        screenshot.save(file_path)
    elif user_platform == "Darwin":  # (Mac OS)
        # Use the screencapture utility to capture the screen with the cursor
        subprocess.run(["screencapture", "-C", file_path])
    else:
        logging.warning(f"The platform you're using ({user_platform}) is not currently supported")

    return send_file(file_path, mimetype='image/png')