import requests
import os
import time

BASE_URL = "http://127.0.0.1:5051"

screenshots_dir = "screenshots"
os.makedirs(screenshots_dir, exist_ok=True)
traces_dir = "traces"
os.makedirs(traces_dir, exist_ok=True)

def test_healthcheck():
    resp = requests.get(f"{BASE_URL}/healthcheck")
    print("Healthcheck:", resp.status_code, resp.json())

def test_launch_browser(headless=False):
    resp = requests.post(f"{BASE_URL}/browser/launch", json={"headless": headless})
    print("Launch browser:", resp.status_code, resp.json())

def test_close_browser():
    resp = requests.post(f"{BASE_URL}/browser/close")
    print("Close browser:", resp.status_code, resp.json())

def test_open_page(url):
    resp = requests.post(f"{BASE_URL}/browser/open", json={"url": url})
    if resp.status_code == 200:
        page_id = resp.json().get("page_id")
        print("Opened page:", resp.status_code, resp.json())
        return page_id
    print("Failed to open page:", resp.status_code, resp.text)
    return None

def test_screenshot(page_id):
    resp = requests.post(f"{BASE_URL}/browser/screenshot", json={"page_id": page_id})
    if resp.status_code == 200:
        screenshot_path = os.path.join(screenshots_dir, f"{page_id}.png")
        with open(screenshot_path, "wb") as f:
            f.write(resp.content)
        print("Screenshot saved at", screenshot_path)
    else:
        print("Failed to take screenshot:", resp.status_code, resp.text)

def test_get_cookies(page_id):
    resp = requests.post(f"{BASE_URL}/browser/get_cookies", json={"page_id": page_id})
    print("Cookies:", resp.status_code, resp.json())

def test_get_local_storage(page_id):
    resp = requests.post(f"{BASE_URL}/browser/get_local_storage", json={"page_id": page_id})
    print("Local storage:", resp.status_code, resp.json())

def test_execute_js(page_id, js_code):
    resp = requests.post(f"{BASE_URL}/browser/execute_js", json={"page_id": page_id, "js": js_code})
    print("Executed JS:", resp.status_code, resp.json())

def test_cdp(page_id, command, params={}):
    resp = requests.post(f"{BASE_URL}/browser/cdp", json={"page_id": page_id, "command": command, "params": params})
    print("CDP Command:", resp.status_code, resp.json())

def test_start_tracing():
    resp = requests.post(f"{BASE_URL}/browser/start_tracing")
    print("Start tracing:", resp.status_code, resp.json())

def test_stop_tracing():
    resp = requests.post(f"{BASE_URL}/browser/stop_tracing")
    if resp.status_code == 200:
        trace_file = resp.json().get("trace_file")
        print("Stop tracing:", resp.status_code, resp.json())
        return trace_file
    print("Failed to stop tracing:", resp.status_code, resp.text)
    return None

def test_download_trace(trace_file):
    resp = requests.get(f"{BASE_URL}/browser/download_trace", params={"trace_file": trace_file})
    if resp.status_code == 200:
        trace_path = os.path.join(traces_dir, os.path.basename(trace_file))
        with open(trace_path, "wb") as f:
            f.write(resp.content)
        print("Trace file saved at", trace_path)
    else:
        print("Failed to download trace:", resp.status_code, resp.text)

def test_get_platform():
    resp = requests.get(f"{BASE_URL}/platform")
    print("Platform info:", resp.status_code, resp.json())

def test_cursor_position():
    resp = requests.get(f"{BASE_URL}/cursor_position")
    print("Cursor position:", resp.status_code, resp.json())

if __name__ == "__main__":
    test_healthcheck()
    # test_launch_browser(headless=False)
    # time.sleep(2)
    # page_id = test_open_page("https://arxiv.org/abs/1706.03762")
    # if page_id:
    #     time.sleep(3)
    #     test_screenshot(page_id)
    #     test_get_cookies(page_id)
    #     test_get_local_storage(page_id)
    #     test_execute_js(page_id, "document.title")
    #     test_cdp(page_id, "Page.getFrameTree", {})
    # test_get_platform()
    # test_cursor_position()
    # test_start_tracing()
    # time.sleep(5)
    # trace_file = test_stop_tracing()
    # if trace_file:
    #     test_download_trace(trace_file)
    # test_close_browser()
