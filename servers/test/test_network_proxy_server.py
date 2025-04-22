import requests

# BASE_URL = "http://127.0.0.1:5052"
# BASE_URL = "http://192.168.5.65:5052"
BASE_URL = "http://win-1.4.155.164.237.nip.io/np"

def test_start_proxy():
    # machine_ip = "192.168.2.114"
    # print(f"Machine IP: {machine_ip}")

    resp = requests.post(f"{BASE_URL}/start", json={
        "filename": "teams-telemetry-1",
        # "storeurl": f"http://{machine_ip}:9200"
    })
    print(resp.status_code)

def test_stop_proxy():
    resp = requests.post(f"{BASE_URL}/stop")
    print(resp.status_code)

def test_status():
    resp = requests.get(f"{BASE_URL}/status")
    print(resp.status_code, resp.json())

if __name__ == "__main__":
    # test_status()

    # test_start_proxy()

    # # import time
    # # time.sleep(15)

    test_stop_proxy() 
