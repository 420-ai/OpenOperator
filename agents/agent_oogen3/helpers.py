import random
import string
from datetime import datetime
import os
from PIL import Image
import os
import json

# from logging_setup import configure_logging

def random_string(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


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
