import requests
import logging
import os
from core.state import State


def open_application(app_name: str, state: State):
    logging.info(f"Opening application: {app_name}")
    computer_control_url = os.environ["COMPUTER_CONTROL_URL"] or "http://localhost:5051"
    requests.post(f"{computer_control_url}/setup/launch", json={"command": "ms-teams"})
