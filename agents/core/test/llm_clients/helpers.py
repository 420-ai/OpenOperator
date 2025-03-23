import base64
import os

def encode_image(image_path):
    full_image_path = os.path.join(os.path.dirname(__file__), image_path)
    with open(full_image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    