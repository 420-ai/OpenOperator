import requests
import logging
import os
from core.state import State


def open_application(app_name: str, state: State):
    logging.info(f"Opening application: {app_name}")
    computer_control_url = os.getenv("COMPUTER_CONTROL_URL", "http://localhost:5050")
    requests.post(f"{computer_control_url}/setup/launch", json={"command": "ms-teams"})
