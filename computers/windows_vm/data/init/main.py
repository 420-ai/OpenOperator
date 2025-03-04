import sys
import os
import json
import requests
import subprocess
import logging
import pythoncom
import glob
import time

# Ensure COM is properly initialized
# pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)

# Setup logging
log_file = os.path.join(".", "logs", "install_software.log")
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")


TEMP_DIR = r"C:\TEMP"
os.makedirs(TEMP_DIR, exist_ok=True)


def log(message):
    print(message)
    logging.info(message)

def extract_ffmpeg(archive_path, extract_to):
    """ Extracts ffmpeg using 7-Zip """
    seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"
    
    if not os.path.exists(seven_zip_path):
        log("7-Zip is required but not found in the expected path. Install 7-Zip first.")
        return False
    
    try:
        subprocess.run([seven_zip_path, 'x', archive_path, f'-o{extract_to}', '-y'], check=True)
        log(f"Extracted ffmpeg to {extract_to}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Error extracting ffmpeg: {e}")
        return False

def update_system_path(new_path):
    """Updates the system PATH variable (requires admin privileges)"""
    try:
        current_path = os.environ["PATH"]
        if new_path not in current_path:
            print(f"Adding {new_path} to system PATH")
            # Append new_path to the current PATH
            updated_path = f"{current_path}{os.pathsep}{new_path}"
            # Use the /M flag to update the system (machine) environment variable
            subprocess.run(['setx', '/M', 'PATH', updated_path], shell=True, check=True)
            print("System PATH updated successfully. A restart may be required for changes to take effect.")
        else:
            print("The specified path is already in the PATH.")
    except Exception as e:
        print(f"Failed to update PATH: {e}")

def find_ffmpeg_bin(root_dir):
    """ Searches for the 'bin' folder inside any 'ffmpeg*' extracted folder. """
    ffmpeg_folders = glob.glob(os.path.join(root_dir, "ffmpeg*"))
    
    if not ffmpeg_folders:
        return None  # No ffmpeg folder found

    for folder in ffmpeg_folders:
        bin_path = os.path.join(folder, "bin")
        if os.path.exists(bin_path) and os.path.isfile(os.path.join(bin_path, "ffmpeg.exe")):
            return bin_path  # Found the correct bin folder

    return None  # No valid bin folder found

def download_and_install(name, mirrors, tools_config):
    if name.lower() == "vs code":
        file_extension = 'exe'
    elif name.lower() == "microsoft teams":
        file_extension = "msi"
    else:
        file_extension = mirrors[0].split('.')[-1]
    
    installer_path = os.path.join(TEMP_DIR, f'{name}_installer.{file_extension}')
    log(f'Downloading {name} ... into {installer_path}')
    
    for url in mirrors:
        try:
            response = requests.get(url, stream=True)
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            log(f'{name} downloaded successfully.')
            break
        except Exception as e:
            log(f'Error downloading from {url}: {e}')
            logging.error(f'Error downloading {name} from {url}: {e}')
    else:
        log(f'Failed to download {name}.')
        return
    

    # FFMPEG
    if name.lower() == "ffmpeg":
        extract_dir = os.path.join(TEMP_DIR, "ffmpeg")
        if extract_ffmpeg(installer_path, extract_dir):
            ffmpeg_bin_path = find_ffmpeg_bin(extract_dir)
            if os.path.exists(ffmpeg_bin_path):
                update_system_path(ffmpeg_bin_path)
            else:
                log("Could not find ffmpeg binary folder after extraction.")
        else:
            log("Failed to extract ffmpeg.")
    
    # ANY OTHER SOFTWARE
    else:
        silent_args = {
            'git': ['/VERYSILENT', '/NORESTART'],
            '7zip': ['/S'],
            'google chrome': ['/silent', '/install'],
            'vs code': ['/VERYSILENT', '/mergetasks=!runcode', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-', '/ACCEPTEULA'],
            'vlc': ['/S'],
            'microsoft teams': ['OPTIONS=noAutoStart=true', 'ALLUSERS=1', '/quiet', '/norestart']
        }
        args = silent_args.get(name.lower(), ['/S'])

        if file_extension == 'exe':
            log(f'Installing {name}...')
            try:
                subprocess.run([installer_path] + args, check=True)
                log(f'{name} installed successfully.')
            except subprocess.CalledProcessError as e:
                log(f'Installation failed for {name}: {e}')
                logging.error(f'Installation failed for {name}: {e}')
        
        elif file_extension == 'msi':
            log(f'Installing {name} (MSI)...')
            try:
                subprocess.run(["msiexec", "/i", installer_path] + args, check=True)
                log(f'{name} installed successfully.')
            except subprocess.CalledProcessError as e:
                log(f'Installation failed for {name}: {e}')
                logging.error(f'Installation failed for {name}: {e}')
    
    # Time sleep for waiting until the installation process is released
    time.sleep(1)
    os.remove(installer_path)

def start_installation():
    json_path = os.path.join(os.path.dirname(__file__), 'software.json')
    
    if not os.path.exists(json_path):
        log('JSON configuration file not found!')
        return
    
    with open(json_path, 'r') as f:
        tools_config = json.load(f)
    
    for tool_name, details in tools_config.items():
        mirrors = details.get('mirrors', [])
        download_and_install(tool_name, mirrors, tools_config)

    log('All tasks completed.')

if __name__ == '__main__':
    try:
        logging.info("Starting Installer...")
        start_installation()
    except Exception as e:
        logging.error(f"Installation failed with error: {e}", exc_info=True)
    finally:
        pythoncom.CoUninitialize()  # Uninitialize COM when exiting
