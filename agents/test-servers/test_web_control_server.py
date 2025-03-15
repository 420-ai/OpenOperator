import requests
import base64
import os

BASE_URL = "http://127.0.0.1:6000"

screenshots_dir = "screenshots"
os.makedirs(screenshots_dir, exist_ok=True)
recordings_dir = "recordings"
os.makedirs(recordings_dir, exist_ok=True)

def test_healthcheck():
    resp = requests.get(f"{BASE_URL}/healthcheck")
    if resp.status_code == 200:
        print("Healthcheck passed:", resp.json())
    else:
        print("Healthcheck failed:", resp.status_code, resp.text)


if __name__ == "__main__":
    test_healthcheck()
