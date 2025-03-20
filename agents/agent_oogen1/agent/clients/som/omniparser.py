import base64
import json
import logging
from pprint import pprint
from typing import Any, Dict, List
import requests
from io import BytesIO
from PIL import Image

logger = logging.getLogger("agent.clients.som.omniparser")

class OmniparserClient:

    def __init__(self):
        logger.debug("Initializing...")
        # Server URL
        self.SERVER_URL = "http://127.0.0.1:8000/parse/"

    # Function to encode image to base64
    def _encode_image(self, image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def _decode_image(self, base64_str) -> Image:
        return Image.open(BytesIO(base64.b64decode(base64_str)))

    # Function to send image to the server
    def _send_image_to_server(self, base64_image):
        payload = json.dumps({"base64_image": base64_image})
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(self.SERVER_URL, data=payload, headers=headers)
        return response.json()

    # Function to save base64 image to file
    def _save_base64_image(self, base64_str, output_file="output.png"):
        image_data = base64.b64decode(base64_str)
        with open(output_file, "wb") as f:
            f.write(image_data)

    def _save_json(self, data, filename="output.json"):
        """
        Saves JSON serializable data to a file.
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # Function to analyze image
    def analyze_image(self, screenshot: Image) -> Dict[str, Any]:
        logger.info("Analysing image...")

        # Shape of the image
        w, h = screenshot.size

        base64_image = self._encode_image(screenshot)
        response = self._send_image_to_server(base64_image)
        
        formatted_output = []
        for i, item in enumerate(response["parsed_content_list"]):
            formatted_output.append({
                "from": "omniparser",
                "type": item["type"],
                "text": item["content"],
                "shape": {
                    "x": int(item["bbox"][0] * w),
                    "y": int(item["bbox"][1] * h),
                    # We need to calculate width as difference between x and x2
                    "width": int((item["bbox"][2] * w) - (item["bbox"][0] * w)),
                    # We need to calculate height as difference between y and y2
                    "height": int((item["bbox"][3] * h) - (item["bbox"][1] * h)),
                },
                "interactivity": item["interactivity"],
            })


        return {
            "parsed_image": self._decode_image(response.get("som_image_base64", "")),
            "parsed_image_base64": response.get("som_image_base64", ""),
            "parsed_content_list": formatted_output,
        }