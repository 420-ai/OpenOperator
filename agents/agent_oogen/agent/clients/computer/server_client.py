from typing import Optional
import requests
import logging
import json
from PIL import Image
import io

logger = logging.getLogger("agent.clients.server_client")

HTTP_SERVER = "http://127.0.0.1:5000"

def execute_python_command(command: str) -> None:
    """
    Executes a python command on the server.
    It can be used to execute the pyautogui commands, or... any other python command. who knows?
    """
    pkgs_prefix: str = "import pyautogui; import time; pyautogui.FAILSAFE = False; {command}"
    # command_list = ["python", "-c", self.pkgs_prefix.format(command=command)]
    command_list = ["pythonw", "-c", pkgs_prefix.format(command=command)]
    payload = json.dumps({"command": command_list, "shell": False})
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(HTTP_SERVER + "/execute", headers=headers, data=payload, timeout=90)
        if response.status_code == 200:
            logger.debug("Command executed successfully: %s", response.text)
        else:
            logger.error("Failed to execute command. Status code: %d", response.status_code)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("An error occurred while trying to execute the command: %s", e)

def get_screenshot() -> Optional[Image.Image]:
        """
        Gets a screenshot from the server. With the cursor.
        """
        response = requests.get(HTTP_SERVER + "/screenshot")
        if response.status_code == 200:
            image = Image.open(io.BytesIO(response.content))
            return image
        else:
            logger.error("Failed to get screenshot. Status code: %d", response.status_code)
            return None
