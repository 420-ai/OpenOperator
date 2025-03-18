from typing import Optional
import requests
import logging
import json
from PIL import Image
import io

logger = logging.getLogger("clients.computer")

class ComputerClient:
    def __init__(self, server_url: str = "http://127.0.0.1:5050"):
        self.server_url = server_url

    def execute_python_command(self, command: str) -> Optional[dict]:
        """
        Executes a python command on the server.
        It can be used to execute pyautogui commands or any other Python command.
        """
        pkgs_prefix: str = "import pyautogui; import time; pyautogui.FAILSAFE = False; {command}"
        command_list = ["pythonw", "-c", pkgs_prefix.format(command=command)]
        payload = json.dumps({"command": command_list, "shell": False})
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(f"{self.server_url}/execute", headers=headers, data=payload, timeout=90)
            
            if response.status_code != 200:
                logger.error("Failed to execute command. Status code: %d", response.status_code)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("An error occurred while trying to execute the command: %s", e)
            return None

    # ----------------------------------
    # Screenshot (image)
    # ----------------------------------

    def get_screenshot(self) -> Optional[Image.Image]:
        """
        Gets a screenshot from the server with the cursor.
        """
        response = requests.get(f"{self.server_url}/screenshot")
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            logger.error("Failed to get screenshot. Status code: %d", response.status_code)
            return None

    # ----------------------------------
    # Recordings (video)
    # ----------------------------------

    def start_recording(self) -> None:
        """
        Starts recording the screen.
        """
        response = requests.post(f"{self.server_url}/start_recording")
        if response.status_code == 200:
            logger.debug("Recording started successfully.")
        else:
            logger.error("Failed to start recording. Status code: %d", response.status_code)

    def end_recording(self) -> None:
        """
        Ends the recording and saves the video.
        """
        response = requests.post(f"{self.server_url}/end_recording")
        if response.status_code == 200:
            logger.debug("Recording ended successfully.")
        else:
            logger.error("Failed to end recording. Status code: %d", response.status_code)

    def get_recording(self, file_path: str) -> None:
        """
        Downloads the recorded video from the server and saves it to the specified file path.
        """
        response = requests.get(f"{self.server_url}/get_recording")
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            logger.debug("Recording saved successfully.")
        else:
            logger.error("Failed to get recording. Status code: %d", response.status_code)

    # ----------------------------------
    # OS Commands
    # ----------------------------------

    def close_all_windows(self) -> None:
        """
        Closes all windows on the server.
        """
        response = requests.post(f"{self.server_url}/setup/close_all")
        if response.status_code == 200:
            logger.debug("All windows closed successfully.")
        else:
            logger.error("Failed to close all windows. Status code: %d", response.status_code)


computer = ComputerClient()