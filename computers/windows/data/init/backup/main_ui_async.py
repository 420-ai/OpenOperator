import sys
import os
import json
import requests
import subprocess
import asyncio
import glob
import logging
import pythoncom
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
)
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
import pyautogui
import traceback
from teams_configurator import TeamsConfigurator
from qasync import QEventLoop, asyncSlot

# Setup logging
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
log_file = os.path.join(desktop_path, "initialization.log")
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

class InstallerSignals(QObject):
    log_signal = pyqtSignal(str)

class InstallerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = InstallerSignals()

        self.initUI()
        
        self.signals.log_signal.connect(self.update_log_ui)
        asyncio.create_task(self.start_installation())
        
    def initUI(self):
        self.setWindowTitle('Software Installer')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        self.log_text_box = QTextEdit()
        self.log_text_box.setReadOnly(True)
        layout.addWidget(self.log_text_box)
        self.setLayout(layout)
    
    def log(self, message):
        self.signals.log_signal.emit(message)
        logging.info(message)

    def update_log_ui(self, message):
        self.log_text_box.append(message)
        QApplication.processEvents()

    async def download_and_install(self, name, mirrors, tools_config):
        temp_dir = os.getenv('TEMP')
        file_extension = 'msi' if name.lower() == "microsoft teams" else mirrors[0].split('.')[-1]
        installer_path = os.path.join(temp_dir, f'{name}_installer.{file_extension}')

        self.log(f'Downloading {name}...')
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
            process = await asyncio.create_subprocess_exec(installer_path, *args)
            await process.wait()
            self.log(f'{name} installed successfully.')

        elif file_extension == 'msi':
            self.log(f'Installing {name} (MSI)...')
            process = await asyncio.create_subprocess_exec("msiexec", "/i", installer_path, *args)
            await process.wait()
            self.log(f'{name} installed successfully.')
            if name.lower() == "microsoft teams":
                await asyncio.sleep(10)
                QTimer.singleShot(0, lambda: self.configure_microsoft_teams(tools_config))
        
        os.remove(installer_path)

    async def start_installation(self):
        json_path = os.path.join(os.path.dirname(__file__), 'software.json')
        if not os.path.exists(json_path):
            self.log('JSON configuration file not found!')
            return
        with open(json_path, 'r') as f:
            tools_config = json.load(f)
        tasks = [self.download_and_install(tool_name, details['mirrors'], tools_config)
                 for tool_name, details in tools_config.items()]
        await asyncio.gather(*tasks)
        self.log('All tasks completed.')

    def configure_microsoft_teams(self, tools_config):
        self.log("Configuring Microsoft Teams...")
        configurator = TeamsConfigurator(self.log)
        images = {
            "setup_complete": os.path.join(os.path.dirname(__file__), "sprucing_things_up_window.png"),
            "sign_in_button": os.path.join(os.path.dirname(__file__), "sign_in_button.png"),
            "all_set": os.path.join(os.path.dirname(__file__), "all_set.png")
        }
        asyncio.create_task(configurator.configure_microsoft_teams(tools_config, images))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    installer = InstallerApp()
    installer.show()

    with loop:
        loop.run_forever()
