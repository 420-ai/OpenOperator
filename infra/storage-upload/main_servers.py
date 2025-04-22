import os
from azure.storage.fileshare import ShareServiceClient, ShareDirectoryClient

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
load_dotenv()

# === Configuration ===
ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
if not ACCOUNT_NAME:
    raise ValueError("AZURE_STORAGE_ACCOUNT_NAME is not set in the environment variables.")

SHARE_NAME = "oo-servers"

# === Only upload these folders ===
ROOT_FOLDER = "../../servers"
SELECTED_FOLDERS = [
    "mcp_server_computer_control",
    "server_computer_control",
    "server_browser_control",
    "server_evaluator",
    "server_network_proxy",
    "server_appium",
    "server_teams_control"
]

# === Init client ===
credential = DefaultAzureCredential()
account_url = f"https://{ACCOUNT_NAME}.file.core.windows.net"
service_client = ShareServiceClient(
    account_url=account_url, 
    credential=credential,
    token_intent="backup")
share_client = service_client.get_share_client(SHARE_NAME)

# Create or use the existing share
try:
    share_client.create_share()
    print(f"Created share: {SHARE_NAME}")
except Exception:
    print(f"Share {SHARE_NAME} already exists")

def upload_dir(current_local_path, current_dir_client: ShareDirectoryClient):
    for item in os.listdir(current_local_path):
        full_local_path = os.path.join(current_local_path, item)
        if os.path.isdir(full_local_path):
            try:
                subdir_client = current_dir_client.create_subdirectory(item)
            except Exception:
                subdir_client = current_dir_client.get_subdirectory_client(item)
                print(f"  Directory {item} already exists, using existing one.")
            upload_dir(full_local_path, subdir_client)
        else:
            with open(full_local_path, "rb") as source_file:
                current_dir_client.upload_file(item, source_file)
                print(f"  Uploaded: {full_local_path}")


def clean_removed_server_folders(share_client, root_folder, selected_folders):
    deleted_files = []
    deleted_dirs = []

    # Get top-level directories in Azure
    root_dir_client = share_client.get_directory_client("")
    remote_items = list(root_dir_client.list_directories_and_files())
    remote_folders = {item['name'] for item in remote_items if item['is_directory']}

    # Delete top-level folders that are no longer selected
    for folder in remote_folders - set(selected_folders):
        try:
            root_dir_client.delete_subdirectory(folder)
            deleted_dirs.append(folder)
        except Exception as e:
            print(f"⚠️ Could not delete {folder}: {e}")

    # Check files within selected folders
    for folder in selected_folders:
        folder_path = os.path.join(root_folder, folder)
        if not os.path.isdir(folder_path):
            continue

        folder_dir_client = root_dir_client.get_subdirectory_client(folder)

        try:
            folder_dir_client.list_directories_and_files()  # This will raise if folder doesn't exist
        except Exception:
            print(f"⚠️ Folder {folder} does not exist in Azure yet, skipping cleanup.")
            continue

        for dirpath, _, filenames in os.walk(folder_path):
            rel_path = os.path.relpath(dirpath, folder_path).replace("\\", "/")
            azure_subdir = folder_dir_client
            if rel_path != ".":
                for part in rel_path.split("/"):
                    azure_subdir = azure_subdir.get_subdirectory_client(part)

            try:
                remote_files = list(azure_subdir.list_directories_and_files())
            except Exception as e:
                print(f"⚠️ Failed to list {rel_path}: {e}")
                continue

            local_files = set(filenames)
            for item in remote_files:
                if not item['is_directory'] and item['name'] not in local_files:
                    try:
                        azure_subdir.delete_file(item['name'])
                        deleted_files.append(os.path.join(folder, rel_path, item['name']).replace("\\", "/"))
                    except Exception as e:
                        print(f"⚠️ Error deleting file {item['name']}: {e}")
                        
    # Logs
    if deleted_files:
        print("\n🗑️ Removed files:")
        for f in deleted_files:
            print(f"  - {f}")

    if deleted_dirs:
        print("\n🗂️ Removed top-level folders:")
        for d in deleted_dirs:
            print(f"  - {d}")

    if not deleted_files and not deleted_dirs:
        print("\n✅ No files or folders to delete.")

def upload_selected_folders_to_directory(share_client, root_folder, selected_folders):
    root_dir_client = share_client.get_directory_client("")

    for folder_name in selected_folders:
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            print(f"Uploading {folder_name} to {SHARE_NAME}...")
            try:
                target_dir_client = root_dir_client.create_subdirectory(folder_name)
            except Exception:
                print(f"Directory {folder_name} already exists in share {SHARE_NAME}")
                target_dir_client = root_dir_client.get_subdirectory_client(folder_name)

            upload_dir(folder_path, target_dir_client)
        else:
            print(f"⚠️ Folder not found: {folder_path}")

if __name__ == "__main__":
    clean_removed_server_folders(share_client, ROOT_FOLDER, SELECTED_FOLDERS)
    upload_selected_folders_to_directory(share_client, ROOT_FOLDER, SELECTED_FOLDERS)
