import sys
import os
import json
import requests
import subprocess
import logging
import pythoncom

# Ensure COM is properly initialized
pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)

# Setup logging
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
log_file = os.path.join(desktop_path, "initialization.log")
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

def log(message):
    print(message)
    logging.info(message)

def download_and_install(name, mirrors, tools_config):
    temp_dir = os.getenv('TEMP')
    
    if name.lower() == "vs code":
        file_extension = 'exe'
    elif name.lower() == "microsoft teams":
        file_extension = "msi"
    else:
        file_extension = mirrors[0].split('.')[-1]
    
    installer_path = os.path.join(temp_dir, f'{name}_installer.{file_extension}')
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
