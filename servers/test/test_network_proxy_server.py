import requests
from utils import get_machine_ip

# BASE_URL = "http://127.0.0.1:5052"
BASE_URL = "http://192.168.5.65:5052"


def test_start_proxy():
    machine_ip = get_machine_ip()

    resp = requests.post(f"{BASE_URL}/start", json={
        "filename": "my-telemetry",
        "storeurl": f"http://{machine_ip}:9200"
    })
    print(resp.status_code)

def test_stop_proxy():
    resp = requests.post(f"{BASE_URL}/stop")
    print(resp.status_code)

def test_status():
    resp = requests.get(f"{BASE_URL}/status")
    print(resp.status_code, resp.json())

if __name__ == "__main__":
    test_status()

    test_start_proxy()

    # import time
    # time.sleep(15)

    # test_stop_proxy() 
