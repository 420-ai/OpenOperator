import sys
import os
import json
import requests
import subprocess
import time
import glob
import logging
import pythoncom
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
)
from pywinauto import Application, Desktop
import pyautogui
import time
import traceback
# from .teams.teams_configurator import TeamsConfigurator



# Ensure COM is properly initialized
# pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)

# Setup logging
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
log_file = os.path.join(desktop_path, "initialization.log")
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

class InstallerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Software Installer')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        
        self.status_label = QLabel('Ready to install software...')
        layout.addWidget(self.status_label)
        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.install_button = QPushButton('Start Installation')
        self.install_button.clicked.connect(self.start_installation)
        layout.addWidget(self.install_button)

        self.setLayout(layout)
    
    def log(self, message):
        self.log_box.append(message)
        logging.info(message)  # Log to file
        QApplication.processEvents()

    def download_and_install(self, name, mirrors, tools_config):
        temp_dir = os.getenv('TEMP')
        
        if name.lower() == "vs code":
            file_extension = 'exe'
        elif name.lower() == "microsoft teams":
            file_extension = "msi"
        else:
            file_extension = mirrors[0].split('.')[-1]
        
        installer_path = os.path.join(temp_dir, f'{name}_installer.{file_extension}')
        self.log(f'Downloading {name} ... into {installer_path}')
        
        for url in mirrors:
            try:
                response = requests.get(url, stream=True)
                with open(installer_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.log(f'{name} downloaded successfully.')
                break
            except Exception as e:
                self.log(f'Error downloading from {url}: {e}')
                logging.error(f'Error downloading {name} from {url}: {e}')
        else:
            self.log(f'Failed to download {name}.')
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
            self.log(f'Installing {name}...')
            try:
                subprocess.run([installer_path] + args, check=True)
                self.log(f'{name} installed successfully.')
            except subprocess.CalledProcessError as e:
                self.log(f'Installation failed for {name}: {e}')
                logging.error(f'Installation failed for {name}: {e}')
        
        elif file_extension == 'msi':
            self.log(f'Installing {name} (MSI)...')
            try:
                subprocess.run(["msiexec", "/i", installer_path] + args, check=True)
                self.log(f'{name} installed successfully.')

                # if name.lower() == "microsoft teams":
                #     configurator = TeamsConfigurator(self.log)
                #     configurator.configure_microsoft_teams(tools_config)    
                
            except subprocess.CalledProcessError as e:
                self.log(f'Installation failed for {name}: {e}')
                logging.error(f'Installation failed for {name}: {e}')
        
        os.remove(installer_path)

    def start_installation(self):
        self.install_button.setDisabled(True)
        json_path = os.path.join(os.path.dirname(__file__), 'software.json')
        
        if not os.path.exists(json_path):
            self.log('JSON configuration file not found!')
            return
        
        with open(json_path, 'r') as f:
            tools_config = json.load(f)
        
        for tool_name, details in tools_config.items():
            mirrors = details.get('mirrors', [])
            self.download_and_install(tool_name, mirrors, tools_config)

        self.status_label.setText('Installation Completed.')
        self.log('All tasks completed.')
        self.install_button.setDisabled(False)

if __name__ == '__main__':
    try:
        logging.info("Starting InstallerApp...")
        app = QApplication(sys.argv)
        installer = InstallerApp()
        installer.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Application failed with error: {e}", exc_info=True)
    finally:
        pythoncom.CoUninitialize()  # Uninitialize COM when exiting
