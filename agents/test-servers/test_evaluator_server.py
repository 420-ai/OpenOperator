import requests

BASE_URL = "http://127.0.0.1:5053"


def test_evaluation():
    resp = requests.post(f"{BASE_URL}/evaluate", json={"text": "Hello, world!"})
    print(resp.status_code)


if __name__ == "__main__":
    test_evaluation()
