import base64
import json
from pprint import pprint
from typing import Dict, List
import requests
from io import BytesIO
from PIL import Image

class OmniparserClient:
    # Server URL
    SERVER_URL = "http://127.0.0.1:8000/parse/"

    # Function to encode image to base64
    def _encode_image(self, image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

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
    def analyze_image(self, screenshot: Image) -> str:
        # Shape of the image
        w, h = screenshot.size

        base64_image = self._encode_image(screenshot)
        response = self._send_image_to_server(base64_image)
        
        if "som_image_base64" in response:
            self._save_base64_image(response["som_image_base64"], "./tmp/parsed_image.png")
        
        if "parsed_content_list" in response:
            self._save_json(response["parsed_content_list"], "./tmp/parsed_content_list.json")


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
            "parsed_image_path": "./tmp/parsed_image.png",
            "parsed_image_base64": response.get("som_image_base64", ""),
            "parsed_content_list": formatted_output,
        }


    # -----------------------------------------
    # Agents related methods
    # -----------------------------------------
    def caption_ents(self, image: Image, ents: List[Dict]):

        # LK_TODO: Add logic for parsing A11y text !!!!!

        for ent in ents:
            pprint(ent)
        

            
        # print("OMNIPARSER - CAPTION_ENTS")
        # print(parsed_content_icon)

        # return parsed_content_icon
        return [] 

    def propose_ents(self, image: Image, with_captions: bool = True) -> List[Dict]:
        """
        Uses the Omniparser client to analyze the image and generate entities.
        The returned list of entities has the same structure as in the original code.
        Since the Omniparser client does not return bounding boxes, each entity is 
        assigned a bounding box that covers the entire image.
        """
        # Use the Omniparser client to analyze the image
        result = self.client.analyze_image(image)

        # print("OMNIPARSER - ANALYZE_IMAGE")
        # print(result["parsed_content_list"])

        return result["parsed_content_list"]
        
        # If the client returns a parsed image file, load it.
        # parsed_image_path = result.get("parsed_image_path")
        # if parsed_image_path:
        #     try:
        #         parsed_image = Image.open(parsed_image_path)
        #     except Exception:
        #         parsed_image = image
        # else:
        #     parsed_image = image

        # width, height = image.size
        # Create one entity per caption returned by the client.
        # Here we assume that all detected entities are text.
        # ents = []
        # for caption in result.get("parsed_content_list", []):
        #     ents.append({
        #         'from': 'omniparser',
        #         'shape': {'x': 0, 'y': 0, 'width': width, 'height': height},
        #         'text': caption if with_captions else '',
        #         'type': 'text'
        #     })
        
        # LK_TODO: IS NOT NEEDED ANYMORE ????
        # If additional captioning is needed (for example if some entities lack text),
        # the caption_ents method can be invoked to update them.
        # if with_captions:
        #     self.caption_ents(image, ents)
        
        # Ensure that the shape values are integers
        # result = [
        #     {
        #         **ent,
        #         "shape": {
        #             "x": int(ent["shape"]["x"]),
        #             "y": int(ent["shape"]["y"]),
        #             "width": int(ent["shape"]["width"]),
        #             "height": int(ent["shape"]["height"])
        #         }
        #     }
        #     for ent in ents
        # ]
        
        # print("OMNIPARSER - PROPOSE_ENTS")
        # print(result)

        # return ents
