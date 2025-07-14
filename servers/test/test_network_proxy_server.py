import requests
import os

# BASE_URL = "http://127.0.0.1:5052"
# BASE_URL = "http://192.168.5.65:5052"
# BASE_URL = "http://win-1.4.155.164.237.nip.io/np"
# BASE_URL = "http://computer-6823417694dd47734aef8fb2.4.242.123.121.nip.io/np"
BASE_URL = "http://comp-7.4.242.123.121.nip.io/np"

telemetry_dir = "telemetry"
os.makedirs(telemetry_dir, exist_ok=True)

def test_healthcheck():
    resp = requests.get(f"{BASE_URL}/healthcheck")
    print("Healthcheck:", resp.status_code, resp.json())


def test_start_proxy(filename: str):
    # machine_ip = "192.168.2.114"
    # print(f"Machine IP: {machine_ip}")

    resp = requests.post(f"{BASE_URL}/start", json={
        "filename": filename,
        # "storeurl": f"http://{machine_ip}:9200"
    })
    print(resp.status_code)

def test_stop_proxy():
    resp = requests.post(f"{BASE_URL}/stop")
    print(resp.status_code)

def test_status():
    resp = requests.get(f"{BASE_URL}/status")
    print(resp.status_code, resp.json())

def test_get_telemetry(filename: str):
    try:
        resp = requests.get(f"{BASE_URL}/get_telemetry", params={"filename": filename})
        print("Get Telemetry:", resp.status_code)

        if resp.status_code == 200:
            # Optionally save the file
            file_path = os.path.join(telemetry_dir, filename)
            with open(file_path, "wb") as f:
                f.write(resp.content)
            print(f"Telemetry file '{filename}' downloaded successfully.")
        else:
            print(f"Failed to fetch telemetry file '{filename}': {resp.status_code}, {resp.text}")

    except Exception as e:
        print(f"Error while fetching telemetry: {e}")

if __name__ == "__main__":
    test_healthcheck()

    test_status()

    test_start_proxy("teams-telemetry-1")

    import time
    time.sleep(15)

    test_stop_proxy() 

    test_status()

    import time
    time.sleep(5)

    test_get_telemetry("teams-telemetry-1.log")
