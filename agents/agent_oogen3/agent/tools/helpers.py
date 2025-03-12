import os
import json
from PIL import Image
from autogen_core.models import UserMessage, SystemMessage
from autogen_core import Image as AutogenImage

def save_image(image: Image.Image, file_path: str,  file_name: str):
    image_file = os.path.join(file_path, file_name)
    image.save(image_file, format="PNG", optimize=True)

def save_json(content: dict, file_path: str, file_name: str):
    json_file = os.path.join(file_path, file_name)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

def save_txt(content: str, file_path: str, file_name: str):
    txt_file = os.path.join(file_path, file_name)
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(content)

def save_system_message(system_message: SystemMessage):
        save_txt(system_message.content, ".", "system_message.txt")

def save_user_message(user_message: UserMessage):
    filtered_messages = [msg for msg in user_message.content if not isinstance(msg, AutogenImage)]
    filtered_messages_str = "\n".join([str(msg) for msg in filtered_messages])
    save_txt(filtered_messages_str, ".", "user_message.txt")
    