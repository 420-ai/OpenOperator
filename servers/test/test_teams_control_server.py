import requests

# BASE_URL = "http://127.0.0.1:5056"
# BASE_URL = "http://192.168.5.65:5056"
# BASE_URL = "http://win-1.4.155.164.237.nip.io/tc"
BASE_URL = "http://comp-6.4.242.123.121.nip.io/tc"


def test_healthcheck():
    resp = requests.get(f"{BASE_URL}/healthcheck")
    print("Healthcheck:", resp.status_code, resp.json())


def test_sign_in():
    resp = requests.post(f"{BASE_URL}/sign_in", json=
                         {
                             "username": "jordan.dalton.oo@outlook.com", 
                             "password": "Some_Very-Secret_Password..?"
                    })
    print(resp.status_code)

def test_configure():
    resp = requests.post(f"{BASE_URL}/configure", json=
                         {
                            "core/localStorageKeyValues": "{\"dG1wLnNldHRpbmdz\":\"eyJ0ZWxlbWV0cnkiOnsiZW5hYmxlQ29tcHJlc3Npb24iOmZhbHNlLCJpc1NpbGVudCI6ZmFsc2UsIm5vcm1hbFByaW9yaXR5U2VuZFRpbWVJblNlY3MiOjIsImhpZ2hQcmlvcml0eVNlbmRUaW1lSW5TZWNzIjoxLCJzYW1wbGluZ1J1bGVzIjp7InNjZW5hcmlvbnMiOnsiKiI6MTAwfSwibG9nZ2luZ25zIjp7IioiOjB9LCJodHRwbnMiOnsiKiI6MH0sImVuZHBvaW50bnMiOnsiKiI6MH0sInVzZXJiaW5zIjp7IioiOjEwMH19LCJlbmFibGVVc2VySWRTYW1wbGluZ1YyIjp0cnVlLCJlbmFibGVCbG9ja1plcm9TYW1wbGluZ1JhdGUiOnRydWV9LCJkaWFnbm9zdGljcyI6eyJpc0RpYWdub3N0aWNzUGFuZWxFbmFibGVkIjp0cnVlLCJkaWFnbm9zdGljc1BhbmVsRW5hYmxlZEFwcHMiOlsiKiJdfSwic2hvcnRjdXRzIjp7ImVuYWJsZURldlNob3J0Y3V0cyI6dHJ1ZX19\"}",
                            "core/devMenuEnabled": True,
                            "app/testModeEnabled": True,
                            "app/remoteDebuggingPort": 9222,
                            "auth/disableSSO": True
                        })
    print(resp.status_code)


if __name__ == "__main__":
    test_healthcheck()
    test_configure()
    # test_sign_in()
    print("do nothing")
