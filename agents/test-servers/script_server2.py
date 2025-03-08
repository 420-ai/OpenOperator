import requests
import base64
import os

# Base URL of the Flask server
BASE_URL = "http://127.0.0.1:5000"

screenshots_dir = "screenshots"
os.makedirs(screenshots_dir, exist_ok=True)
recordings_dir = "recordings"
os.makedirs(recordings_dir, exist_ok=True)

def test_platform():
    resp = requests.get(f"{BASE_URL}/platform")
    print("Platform:", resp.text)

def test_cursor_position():
    resp = requests.get(f"{BASE_URL}/cursor_position")
    print("Cursor Position:", resp.text)

def test_screen_size():
    resp = requests.post(f"{BASE_URL}/screen_size")
    print("Screen Size:", resp.json())

def test_obs_winagent():
    resp = requests.get(f"{BASE_URL}/obs_winagent")
    data = resp.json()
    if data['status'] == 'success':
        img_data = base64.b64decode(data['image'])

        file_path = os.path.join(screenshots_dir, "winagent.png")
        with open(file_path, "wb") as f:
            f.write(img_data)
        print("OBS WinAgent screenshot saved as winagent.png")
    else:
        print("OBS WinAgent Error:", data['message'])

def test_execute_command_windows():
    command = "print('Hello from server!')"
    resp = requests.post(f"{BASE_URL}/execute_windows", json={"command": command})
    print("Execute Command Response:", resp.json())

def test_list_directory():
    resp = requests.post(f"{BASE_URL}/list_directory", json={"path": "."})
    print("Directory Tree:", resp.json())

def test_capture_screen_with_cursor():
    resp = requests.get(f"{BASE_URL}/screenshot")
    file_path = os.path.join(screenshots_dir, "screenshot.png")
    with open(file_path, "wb") as f:
        f.write(resp.content)
    print("Screenshot with cursor saved as screenshot.png")

def test_start_end_recording():
    # Start recording
    resp_start = requests.post(f"{BASE_URL}/start_recording")
    print("Start Recording:", resp_start.json())

    import time
    time.sleep(10)  # Record for 5 seconds

    # End recording
    resp_end = requests.post(f"{BASE_URL}/end_recording")
    print("End Recording:", resp_end.json())

    # Download recording
    resp_get = requests.get(f"{BASE_URL}/get_recording")
    if resp_get.status_code == 200:
        file_path = os.path.join(recordings_dir, "recording.mp4")
        with open(file_path, "wb") as f:
            f.write(resp_get.content)
        print("Recording downloaded successfully.")
    else:
        print("Failed to download recording:", resp_get.json())

def end_recording():
    resp_end = requests.post(f"{BASE_URL}/end_recording")
    if resp_end.status_code == 200:
        print("Recording ended successfully.")
    else:
        print("Failed to end recording. Status code:", resp_end.status_code)

def test_activate_window():
    resp = requests.post(f"{BASE_URL}/setup/activate_window", json={"window_name": "Notepad"})
    print("Activate Window:", resp.text)

def test_close_all_windows():
    resp = requests.post(f"{BASE_URL}/setup/close_all")
    print("Close All Windows:", resp.text)

if __name__ == "__main__":
    # test_platform()
    # test_cursor_position()
    # test_screen_size()
    # test_obs_winagent()
    # test_execute_command_windows()
    # test_list_directory()
    # test_capture_screen_with_cursor()
    # test_start_end_recording()
    end_recording()
    # test_activate_window()
    # Uncomment the line below if you are sure you want to close all windows.
    # test_close_all_windows()
