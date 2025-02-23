import sys
import os
import json
import requests
import subprocess
import time
import glob
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
)

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
            try:
                subprocess.run([installer_path] + args, check=True)
                self.log(f'{name} installed successfully.')
            except subprocess.CalledProcessError as e:
                self.log(f'Installation failed for {name}: {e}')
        
        elif file_extension == 'msi':
            self.log(f'Installing {name} (MSI)...')
            try:
                subprocess.run(["msiexec", "/i", installer_path] + args, check=True)
                self.log(f'{name} installed successfully.')
                if name.lower() == "microsoft teams":
                    self.configure_microsoft_teams(tools_config)
            except subprocess.CalledProcessError as e:
                self.log(f'Installation failed for {name}: {e}')
        
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

    def configure_microsoft_teams(self, tools_config):
        self.log("Configuring Microsoft Teams...")

        powershell_script = r"""
        $teamsRegistryPath = 'HKCU:\\Software\\Microsoft\\Office\\Teams'
        if (!(Test-Path $teamsRegistryPath)) {
            New-Item -Path $teamsRegistryPath -Force
        }
        Set-ItemProperty -Path $teamsRegistryPath -Name 'IsLoggedOut' -Value 0 -Type DWord
        Set-ItemProperty -Path $teamsRegistryPath -Name 'FirstRun' -Value 0 -Type DWord
        Set-ItemProperty -Path $teamsRegistryPath -Name 'HideWelcomeScreen' -Value 1 -Type DWord
        """
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-NoProfile", "-Command", powershell_script], check=True)

        username = tools_config["Microsoft Teams"]["user"]["name"]
        password = tools_config["Microsoft Teams"]["user"]["password"]

        subprocess.run(["cmdkey", "/generic:MicrosoftOffice16_Data:SSPI:teams.microsoft.com", f"/user:{username}", f"/pass:{password}"], check=True)
        self.log("Microsoft Teams configured and credentials stored successfully.")

        teams_path = r"C:\\Program Files (x86)\\Microsoft\\Teams\\current\\Teams.exe"
        if os.path.exists(teams_path):
            subprocess.Popen([teams_path])
            self.log("Microsoft Teams launched successfully.")
        else:
            self.log("Error: Teams executable not found. Please verify the installation path.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    installer = InstallerApp()
    installer.show()
    sys.exit(app.exec_())
