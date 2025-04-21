import requests

def check_appium_server(url="http://127.0.0.1:4723"):
    try:
        response = requests.get(f"{url}/status", timeout=5)
        if response.status_code == 200:
            print("✅ Appium server is running!")
            print("Status:", response.json())
        else:
            print(f"⚠️ Appium server responded with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to Appium server: {e}")

if __name__ == "__main__":
    check_appium_server()
