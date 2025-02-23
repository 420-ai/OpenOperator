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
from PyQt5.QtCore import pyqtSignal, QObject
import threading
import pyautogui
import traceback

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
        
        # Connect signals to respective slots
        self.signals.log_signal.connect(self.update_log_ui)
        
        threading.Thread(target=self.start_installation, daemon=True).start()
        
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
        try:
            self.wait_for_teams_setup_to_complete()
            self.log('Starting installation...')
        except Exception as e:
            self.log(f'Error: {e}')

        json_path = os.path.join(os.path.dirname(__file__), 'software.json')
        
        if not os.path.exists(json_path):
            self.log('JSON configuration file not found!')
            return
        
        with open(json_path, 'r') as f:
            tools_config = json.load(f)
        
        for tool_name, details in tools_config.items():
            mirrors = details.get('mirrors', [])
            self.download_and_install(tool_name, mirrors, tools_config)

        self.log('All tasks completed.')

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    # TEAMS
    # ----------------------------------------------------------------
    # ----------------------------------------------------------------

    def find_teams_executable(self):
        windows_apps_path = r"C:\Program Files\WindowsApps"
        teams_exe_pattern = os.path.join(windows_apps_path, "MSTeams_*", "ms-teams.exe")

        teams_paths = glob.glob(teams_exe_pattern)  
        if teams_paths:
            return teams_paths[0]  

        return None  

    def launch_teams(self):
        teams_path = self.find_teams_executable()
        
        if teams_path:
            self.log(f"Launching Microsoft Teams from: {teams_path}")
            subprocess.Popen([teams_path])
        else:
            self.log("Error: Microsoft Teams executable not found.")

    def press_enter(self):
        time.sleep(2)  # Wait for Teams to load
        pyautogui.press("enter")  # Press enter to confirm setup

    def wait_for_teams_setup_to_complete(self):
        self.log("Waiting for Teams setup window to disappear...")
        image_path = os.path.join(os.path.dirname(__file__), "sprucing_things_up_window.png")

        try:
            while True:

                window_found = pyautogui.locateOnScreen(image_path, confidence=0.8)

                if not window_found:
                    self.log("Teams setup completed.")
                    break

                time.sleep(1)

        except Exception as e:
            logging.error(f'Error: {e}')
            traceback_str = traceback.format_exc()
            logging.error(traceback_str)

    def close_teams_popup(self):
        self.log("Attempting to close the next popup window...")
        # Send Alt + F4 to close the active window
        pyautogui.hotkey("alt", "f4")
        self.log("Sent 'Alt + F4' to close the window.")

    def click_sign_in_button(self):
        self.log("Attempting to click 'Sign in' button...")
        
        try:
            # Locate the "Sign in" button on the screen
            button_location = pyautogui.locateCenterOnScreen("sign_in_button.png", confidence=0.8)

            if button_location:
                pyautogui.moveTo(button_location, duration=1)
                pyautogui.click()
                self.log("Clicked 'Sign in' button successfully.")
            else:
                self.log("Error: Could not find 'Sign in' button on the screen.")

        except Exception as e:
            logging.error(f"Failed to interact with Teams sign-in screen: {e}")

    def enter_teams_username(self, tools_config):
        self.log("Entering Teams username...")

        # Get username from software.json
        teams_config = tools_config.get("Microsoft Teams", {}).get("user", {})
        username = teams_config.get("name", "")

        if username:
            pyautogui.write(username)
            pyautogui.press("enter")
            self.log("Entered Teams username successfully.")
        else:
            self.log("No username found in software.json")

    def enter_teams_password(self, tools_config):
        self.log("Entering Teams password...")

        # Get password from software.json
        teams_config = tools_config.get("Microsoft Teams", {}).get("user", {})
        password = teams_config.get("password", "")

        if password:
            pyautogui.write(password)
            pyautogui.press("enter")
            self.log("Entered Teams password successfully.")
        else:
            self.log("No password found in software.json")

    def wait_for_all_set_window(self, timeout=30):
        start_time = time.time()

        while time.time() - start_time < timeout:
            window_found = pyautogui.locateOnScreen("all_set.png", confidence=0.8)

            if window_found:
                self.log("Window detected!")
                return True
            
            time.sleep(1)  # Check again after 1 second

        self.log("Timeout: Window not found.")
        return False

    def configure_microsoft_teams(self, tools_config):
        self.log("Configuring Microsoft Teams...")

        try:
            self.log("Launching Microsoft Teams...")
            self.launch_teams()
            time.sleep(5)

            # Automate clicking "Finish Setup"
            self.log("Clicking 'Finish Setup'...")
            self.press_enter()

            # Wait for the next window to appear
            self.log("Waiting for Teams setup to complete...")
            self.wait_for_teams_setup_to_complete()

            # Automate clicking "Sign in" button
            self.log("Clicking 'Sign in' button...")
            self.click_sign_in_button()
            time.sleep(5)

            # Enter username
            self.log("Entering Teams username...")
            self.enter_teams_username(tools_config)
            self.press_enter()
            time.sleep(5)

            # Enter password
            self.log("Entering Teams password...")
            self.enter_teams_password(tools_config)
            self.press_enter()
            time.sleep(5)

            # Click Enter to confirm
            self.press_enter()

            # Wait until "All set"
            self.log("Waiting for 'All set' window to appear...")
            self.wait_for_all_set_window()
            self.press_enter()

            self.log("Microsoft Teams configured successfully.")
        except Exception as e:
            self.log(f"Error configuring Teams: {e}")
            logging.error(f"Error configuring Teams: {e}")

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
        pythoncom.CoUninitialize()
