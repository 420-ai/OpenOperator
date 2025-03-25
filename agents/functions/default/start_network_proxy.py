import requests
import logging
import os

def start_network_proxy():
    network_proxy_control_url = os.environ["NETWORK_PROXY_CONTROL_URL"]
    requests.post(f"{network_proxy_control_url}/start")
    logging.info("Network proxy server started.")
