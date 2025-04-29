import os

def check_file_exists(path, file_name):
    full_path = os.path.join(path, file_name)
    return {"exists": os.path.exists(full_path)}
