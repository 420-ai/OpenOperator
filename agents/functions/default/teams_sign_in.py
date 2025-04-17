import requests
import logging
import os
import time
from core.state import State


def teams_sign_in(state: State):
    apm = state.get_apm_state()

    accounts = apm["accounts"]
    if not accounts or len(accounts) == 0:
        raise ValueError("No accounts found in APM state.")

    test_account = accounts[0]

    logging.info(f"Signing in to Teams with username: {test_account["Username"]}")
    teams_control_url = os.getenv("TEAMS_CONTROL_URL", "http://localhost:5056")

    response = requests.post(
        f"{teams_control_url}/sign_in",
        json={"username": test_account["Username"], "password": test_account["Password"]},
    )

    time.sleep(20)

    if response.status_code != 200:
        logging.error(f"Failed to sign in to Teams: {response.text}")
        raise Exception(f"Failed to sign in to Teams: {response.text}")
    
    logging.info(f"Signed in to Teams with username: {test_account["Username"]}")
