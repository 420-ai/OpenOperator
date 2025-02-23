import requests

# Server configuration
SERVER_URL = 'http://localhost:6000'

def test_home():
    response = requests.get(SERVER_URL + '/')
    if response.status_code == 200:
        print('Home endpoint:', response.text)
    else:
        print('Home endpoint failed:', response.status_code)

def test_endpoint():
    response = requests.get(SERVER_URL + '/test')
    if response.status_code == 200:
        print('Test endpoint:', response.json())
    else:
        print('Test endpoint failed:', response.status_code)

if __name__ == '__main__':
    print('Testing server endpoints...')
    test_home()
    test_endpoint()
