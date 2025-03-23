import base64
import random
import string
from datetime import datetime
import os
from typing import Any, List
from PIL import Image
import os
import json
import io
import copy

def random_string(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def save_image(image: Image.Image, file_path: str,  file_name: str):
    image_file = os.path.join(file_path, file_name)
    image.save(image_file, format="PNG", optimize=True)

def save_txt(content: str, file_path: str, file_name: str):
    txt_file = os.path.join(file_path, file_name)
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(content)

def save_json(content: dict, file_path: str, file_name: str):
    json_file = os.path.join(file_path, file_name)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

def fm(message:str):
    return f"\n<><><><><><><><><><><><><><><><><><><><><><>\n{message}\n<><><><><><><><><><><><><><><><><><><><><><>"


def resize_and_compress_image(image: Image.Image, max_size=(1024, 1024)) -> Image.Image:
    """
    Resizes and compresses a PNG image while maintaining quality.

    :param image: PIL Image to be resized and compressed.
    :param max_size: Maximum width and height as a tuple.
    :return: Resized and compressed PIL Image.
    """
    # Resize while keeping the aspect ratio
    image = image.copy()  # Ensure we're not modifying the original image
    image.thumbnail(max_size, Image.LANCZOS)
    
    # Save the image into a BytesIO buffer to re-load it (ensures proper compression)
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG", optimize=True)
    img_bytes.seek(0)

    # Return the compressed image
    return Image.open(img_bytes)



# Custom related
def format_messages(messages: list[dict]):
    messages_copy = copy.deepcopy(messages)  # Create a deep copy to avoid modifying the original list
    
    for message in messages_copy:
        if "content" in message and isinstance(message["content"], list):
            for content_item in message["content"]:
                if content_item.get("type") == "image_url" and "image_url" in content_item:
                    content_item["image_url"]["url"] = "<BASE64_IMAGE>"
    
    return messages_copy
