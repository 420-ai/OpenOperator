import requests

BASE_URL = "http://127.0.0.1:5052"


def test_start_proxy():
    resp = requests.post(f"{BASE_URL}/start")
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

    import time
    time.sleep(3)

    test_stop_proxy() 
