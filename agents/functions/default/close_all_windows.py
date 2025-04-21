import requests
import logging
import os

def close_all_windows():
    logging.info("Close all windows")
    computer_control_url = os.getenv("COMPUTER_CONTROL_URL","http://localhost:5050")
    requests.post(f"{computer_control_url}/setup/close_all")
