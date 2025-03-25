import base64
from PIL import Image
import io
import copy

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


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
                if content_item.get("type") == "image" and "data" in content_item:
                    content_item["data"] = "<BASE64_IMAGE>"
    
    return messages_copy
