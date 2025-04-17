import requests

BASE_URL = "http://127.0.0.1:5056"


def test_sign_in():
    resp = requests.post(f"{BASE_URL}/sign_in", json=
                         {
                             "username": "jordan.dalton.oo@outlook.com", 
                             "password": "Some_Very-Secret_Password..?"
                    })
    print(resp.status_code)


if __name__ == "__main__":
    test_sign_in()
