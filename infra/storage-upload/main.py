import os
from azure.storage.fileshare import ShareServiceClient, ShareDirectoryClient
from dotenv import load_dotenv
load_dotenv()

# === Configuration ===
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not AZURE_STORAGE_CONNECTION_STRING:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set in the environment variables.")


# === Only upload these folders ===
ROOT_FOLDER = "../../servers"
SELECTED_FOLDERS = [
    "mcp_server_computer_control",
    "server_browser_control",
    "server_computer_control",
    "server_evaluator",
    "server_network_proxy"
]

# === Init client ===
service_client = ShareServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def upload_folder_to_share(local_folder, share_name):
    print(f"Creating share: {share_name}")
    share_client = service_client.get_share_client(share_name)
    try:
        share_client.create_share()
    except Exception:
        print(f"Share {share_name} already exists")

    def upload_dir(current_local_path, current_dir_client: ShareDirectoryClient):
        for item in os.listdir(current_local_path):
            full_local_path = os.path.join(current_local_path, item)
            if os.path.isdir(full_local_path):
                subdir_client = current_dir_client.create_subdirectory(item)
                upload_dir(full_local_path, subdir_client)
            else:
                with open(full_local_path, "rb") as source_file:
                    current_dir_client.upload_file(item, source_file)
                    print(f"  Uploaded: {full_local_path}")

    root_dir_client = share_client.get_directory_client("")
    upload_dir(local_folder, root_dir_client)

def upload_selected_folders(root_folder, selected_folders):
    for folder_name in selected_folders:
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            share_name = folder_name.lower().replace("_", "-")
            upload_folder_to_share(folder_path, share_name)
        else:
            print(f"⚠️ Folder not found: {folder_path}")

if __name__ == "__main__":
    upload_selected_folders(ROOT_FOLDER, SELECTED_FOLDERS)
