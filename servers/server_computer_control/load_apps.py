import json
import os

def load_app_paths(json_path: str) -> dict:
    with open(json_path, 'r') as f:
        apps = json.load(f)

    username = os.getlogin()
    for key, value in apps.items():
        if isinstance(value, str):
            apps[key] = value.replace("USERNAME", username)
    return apps