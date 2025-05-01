import os
from azure.storage.fileshare import ShareServiceClient, ShareDirectoryClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
load_dotenv()

# === Configuration ===
ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
if not ACCOUNT_NAME:
    raise ValueError("AZURE_STORAGE_ACCOUNT_NAME is not set in the environment variables.")


SHARE_NAME = "windows-data"

# === Map of local path -> destination path in Azure File Share ===
SELECTED_PATHS = {
    "../../computers/windows/docker/scripts/install.bat": "oem/install.bat",
    "../../computers/windows/docker/data/init": "data/init",
}

# === Init client ===
credential = DefaultAzureCredential()
account_url = f"https://{ACCOUNT_NAME}.file.core.windows.net"
service_client = ShareServiceClient(
    account_url=account_url, 
    credential=credential,
    token_intent="backup")
share_client = service_client.get_share_client(SHARE_NAME)

try:
    share_client.create_share()
    print(f"Created share: {SHARE_NAME}")
except Exception:
    print(f"Share {SHARE_NAME} already exists")

def ensure_remote_directory(path, base_dir_client):
    """Walks and creates necessary subdirectories, returns final dir client."""
    path_parts = path.strip("/").split("/")
    current = base_dir_client
    for part in path_parts:
        try:
            current = current.create_subdirectory(part)
        except Exception:
            current = current.get_subdirectory_client(part)
    return current

def upload_file(local_path, dest_path, share_client):
    dest_dir, filename = os.path.split(dest_path)
    base_dir_client = share_client.get_directory_client("")
    target_dir_client = ensure_remote_directory(dest_dir, base_dir_client)

    with open(local_path, "rb") as f:
        target_dir_client.upload_file(filename, f)
        print(f"Uploaded file: {local_path} → {dest_path}")

def upload_directory(local_dir, dest_dir, share_client):
    for root, dirs, files in os.walk(local_dir):
        rel_root = os.path.relpath(root, local_dir)
        remote_subdir = os.path.normpath(os.path.join(dest_dir, rel_root)).replace("\\", "/")

        base_dir_client = share_client.get_directory_client("")
        target_dir_client = ensure_remote_directory(remote_subdir, base_dir_client)

        for file in files:
            full_path = os.path.join(root, file)
            with open(full_path, "rb") as f:
                target_dir_client.upload_file(file, f)
                print(f"  Uploaded: {full_path} → {remote_subdir}/{file}")

def upload_selected_paths(selected_paths, share_client):
    for local_path, dest_path in selected_paths.items():
        if os.path.isfile(local_path):
            upload_file(local_path, dest_path, share_client)
        elif os.path.isdir(local_path):
            upload_directory(local_path, dest_path, share_client)
        else:
            print(f"⚠️ Path not found: {local_path}")

def list_all_paths(share_client):
    """Recursively lists all file and directory paths in the share."""
    paths = set()

    def walk_directory(dir_client, current_path=""):
        items = dir_client.list_directories_and_files()
        for item in items:
            full_path = os.path.join(current_path, item['name']).replace("\\", "/")
            paths.add(full_path)
            if item['is_directory']:
                sub_dir_client = dir_client.get_subdirectory_client(item['name'])
                walk_directory(sub_dir_client, full_path)

    root_dir_client = share_client.get_directory_client("")
    walk_directory(root_dir_client)
    return paths

def delete_directory_recursive(dir_client: ShareDirectoryClient, path=""):
    try:
        items = list(dir_client.list_directories_and_files())
    except Exception as e:
        print(f"⚠️ Cannot list {path or dir_client.path}: {e}")
        return

    for item in items:
        item_path = os.path.join(path, item["name"]).replace("\\", "/")
        try:
            if item["is_directory"]:
                sub_dir_client = dir_client.get_subdirectory_client(item["name"])
                delete_directory_recursive(sub_dir_client, item_path)
                dir_client.delete_subdirectory(item["name"])
                print(f"🗂️ Deleted directory: {item_path}")
            else:
                dir_client.delete_file(item["name"])
                print(f"🗑️ Deleted file: {item_path}")
        except Exception as e:
            print(f"⚠️ Error deleting {item_path}: {e}")

def clean_removed_paths(selected_paths, share_client):
    current_paths = set()

    for local_path, dest_path in selected_paths.items():
        if os.path.isfile(local_path):
            current_paths.add(dest_path)
        elif os.path.isdir(local_path):
            for root, dirs, files in os.walk(local_path):
                rel_root = os.path.relpath(root, local_path)
                for file in files:
                    remote_path = os.path.normpath(os.path.join(dest_path, rel_root, file)).replace("\\", "/")
                    current_paths.add(remote_path)

    remote_paths = list_all_paths(share_client)

    to_delete = remote_paths - current_paths
    for path in sorted(to_delete, reverse=True):  # delete deeper files/folders first
        dir_path, filename = os.path.split(path)
        dir_client = share_client.get_directory_client(dir_path)

        try:
            if path in current_paths:
                continue
            try:
                file_path = os.path.join(dir_path, filename).replace("\\", "/")
                if "." in filename:  # Better check for files
                    dir_client.delete_file(filename)
                    print(f"🗑️ Deleted file: {path}")
                else:
                    sub_dir_client = share_client.get_directory_client(path)
                    delete_directory_recursive(sub_dir_client, path)
                    dir_client.delete_subdirectory(filename)
                    print(f"🗂️ Deleted directory: {path}")
            except Exception as e:
                print(f"⚠️ Error deleting {path}: {e}")
        except Exception as e:
            print(f"⚠️ Error deleting {path}: {e}")


if __name__ == "__main__":
    clean_removed_paths(SELECTED_PATHS, share_client)
    upload_selected_paths(SELECTED_PATHS, share_client)
    print("Upload complete.")