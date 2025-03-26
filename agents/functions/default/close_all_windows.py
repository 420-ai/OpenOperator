import requests
import logging
import os

def close_all_windows():
    logging.info("Close all windows")
    computer_control_url = os.environ["COMPUTER_CONTROL_URL"] or "http://localhost:5051"
    requests.post(f"{computer_control_url}/setup/close_all")
