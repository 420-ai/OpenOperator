import requests
import logging
import os

def stop_network_proxy():
    network_proxy_control_url = os.getenv("NETWORK_PROXY_CONTROL_URL", "http://localhost:5052")
    requests.post(f"{network_proxy_control_url}/stop")
    logging.info("Network proxy server stopped.")
