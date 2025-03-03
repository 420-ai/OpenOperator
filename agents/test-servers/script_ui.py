import os
import base64
import requests
import json
from io import BytesIO
from PIL import Image

def load_image_as_base64(image_path):
    """
    Loads an image from a file and returns it as a base64-encoded PNG string.
    """
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        base64_str = base64.b64encode(img_bytes).decode("utf-8")
    return base64_str

def send_parse_request(server_url, base64_image):
    """
    Sends a POST request to the server's /parse/ endpoint with the base64 image.
    """
    payload = {"base64_image": base64_image}
    try:
        response = requests.post(f"{server_url}/parse/", json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def save_base64_to_png(base64_str, filename):
    """
    Saves a base64-encoded PNG image to a file.
    """
    img_data = base64.b64decode(base64_str)
    with open(filename, "wb") as f:
        f.write(img_data)
    print(f"Saved image to {filename}")

def save_json(data, filename):
    """
    Saves JSON serializable data to a file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved JSON data to {filename}")

if __name__ == "__main__":
    # URL of the running Omniparser server
    server_url = "http://localhost:8000"

    # Load image from file and convert it to base64
    image_path = "./test/screenshot.png"
    base64_image = load_image_as_base64(image_path)

    # Send the image to the server for parsing
    result = send_parse_request(server_url, base64_image)

    if result:
        # Save som_image_base64 into a PNG file
        if "som_image_base64" in result:
            save_base64_to_png(result["som_image_base64"], "./test/som_image.png")
        else:
            print("som_image_base64 not found in the response.")

        # Save parsed_content_list into a JSON file
        if "parsed_content_list" in result:
            save_json(result["parsed_content_list"], "./test/parsed_content_list.json")
        else:
            print("parsed_content_list not found in the response.")
    else:
        print("Failed to get a valid response from the server.")
