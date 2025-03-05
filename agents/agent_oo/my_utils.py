import json
import base64
from PIL import Image
import io
import os

if not os.path.exists('tmp'):
    os.makedirs('tmp')

def save_to_json(data: list, filename: str) -> None:
    """
    Saves a list of dictionaries into a JSON file with properly formatted keys.
    
    :param data: List of dictionaries to save
    :param filename: Name of the JSON file
    """
    with open(f"tmp/{filename}", 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def save_base64_to_png(base64_string: str, filename: str) -> None:
    """
    Decodes a base64-encoded string and saves it as a PNG file.
    
    :param base64_string: Base64-encoded image data
    :param filename: Name of the output PNG file
    """
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    image.save(f"tmp/{filename}", "PNG")

def save_image(image: Image, filename: str) -> None:
    """
    Saves an image to a file.
    
    :param image: Image to save
    :param filename: Name of the output file
    """
    image.save(f"tmp/{filename}", "PNG")