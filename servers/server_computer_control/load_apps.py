import json
import os

def load_app_paths(json_filename: str) -> dict:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, json_filename)

    with open(json_path, 'r') as f:
        apps = json.load(f)

    username = os.getlogin()
    for key, value in apps.items():
        if isinstance(value, str):
            apps[key] = value.replace("USERNAME", username)
    return apps