import logging
import io
import os
from typing import Optional, Dict
from PIL import Image
import requests

logger = logging.getLogger("core.clients.browser")

class BrowserClient:
    def __init__(self):
        self.server_url = os.getenv("BROWSER_CONTROL_URL", "http://127.0.0.1:5051")

    def browser_launch(self, headless: bool = False) -> None:
        resp = requests.post(f"{self.server_url}/browser/launch", json={"headless": headless})
        logger.debug("Launch browser:", resp.status_code, resp.json())

    def browser_close(self) -> None:
        resp = requests.post(f"{self.server_url}/browser/close")
        logger.debug("Close browser:", resp.status_code, resp.json())

    def open_page(self, url: str) -> Optional[str]:
        resp = requests.post(f"{self.server_url}/browser/open", json={"url": url})
        if resp.status_code == 200:
            page_id = resp.json().get("page_id")
            logger.debug("Opened page:", resp.status_code, resp.json())
            return page_id
        logger.debug("Failed to open page:", resp.status_code, resp.text)
        return None

    def test_screenshot(self, page_id: str) -> Optional[Image.Image]:
        response = requests.post(f"{self.server_url}/browser/screenshot", json={"page_id": page_id})
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        logger.error("Failed to get screenshot. Status code: %d", response.status_code)
        return None

    def get_cookies(self, page_id: str) -> Dict:
        resp = requests.post(f"{self.server_url}/browser/get_cookies", json={"page_id": page_id})
        logger.debug("Cookies:", resp.status_code, resp.json())
        return resp.json()

    def get_local_storage(self, page_id: str) -> Dict:
        resp = requests.post(f"{self.server_url}/browser/get_local_storage", json={"page_id": page_id})
        logger.debug("Local storage:", resp.status_code, resp.json())
        return resp.json()

    def execute_js(self, page_id: str, js_code: str) -> Dict:
        resp = requests.post(f"{self.server_url}/browser/execute_js", json={"page_id": page_id, "js": js_code})
        logger.debug("Executed JS:", resp.status_code, resp.json())
        return resp.json()

    def cdp(self, page_id: str, command: str, params: Dict = {}) -> Dict:
        resp = requests.post(f"{self.server_url}/browser/cdp", json={"page_id": page_id, "command": command, "params": params})
        logger.debug("CDP Command:", resp.status_code, resp.json())
        return resp.json()

    def start_tracing(self) -> Dict:
        resp = requests.post(f"{self.server_url}/browser/start_tracing")
        logger.debug("Start tracing:", resp.status_code, resp.json())
        return resp.json()

    def stop_tracing(self) -> Optional[str]:
        resp = requests.post(f"{self.server_url}/browser/stop_tracing")
        if resp.status_code == 200:
            trace_file = resp.json().get("trace_file")
            logger.debug("Stop tracing:", resp.status_code, resp.json())
            return trace_file
        logger.debug("Failed to stop tracing:", resp.status_code, resp.text)
        return None

    def download_trace(self, trace_file: str, file_path: str) -> None:
        resp = requests.get(f"{self.server_url}/browser/download_trace", params={"trace_file": trace_file})
        if resp.status_code == 200:
            trace_path = os.path.join(file_path)
            with open(trace_path, "wb") as f:
                f.write(resp.content)
            logger.debug("Trace file saved at", trace_path)
        else:
            logger.debug("Failed to download trace:", resp.status_code, resp.text)

    def get_platform(self) -> Dict:
        resp = requests.get(f"{self.server_url}/platform")
        logger.debug("Platform info:", resp.status_code, resp.json())
        return resp.json()

    def get_cursor_position(self) -> Dict:
        resp = requests.get(f"{self.server_url}/cursor_position")
        logger.debug("Cursor position:", resp.status_code, resp.json())
        return resp.json()
