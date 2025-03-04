import os
import subprocess
import time
import glob
import logging
import pyautogui
import time
import traceback
import re
import win32gui
from helpers import wait_for_window, wait_for_window_to_disappear


class TeamsConfigurator:
    def __init__(self, log_function):
        self.log = log_function

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

    def wait_for_teams_setup_window(self):
        window_nickname = "Sprucing things up"
        self.log(f"Wating for window '{window_nickname}' ...")
        hwnd = wait_for_window(self, window_title_substring="", window_class="EdgeUiInputTopWndClass" )

        if hwnd:
            self.log(f"Successfully detected window '{window_nickname}'")
        else:
            self.log(f"Failed to detect window '{window_nickname}' within the timeout.")


        # self.log(os.getcwd())
        # script_dir = os.path.abspath(os.path.dirname(__file__))
        # self.log(f"Script directory: {script_dir}")
        # image_path = os.path.join(os.path.dirname(__file__), "sprucing_things_up_window.png")
        # self.log(f"Image path: {image_path}")
        # self.log(f"Image exists: {os.path.exists(image_path)}")
        
        # while True:
        #     try:
        #         self.log_all_visible_windows()

        #         hwnd = wait_for_window(self, window_title_substring="Sprucing things up")

        #         window_found = pyautogui.locateOnScreen(image_path, confidence=0.8)

        #         if window_found:
        #             self.log("'Sprucing things up' window appeared!")
        #             break  # Image found; exit loop

        #         else:
        #             self.log("'Sprucing things up' window not yet visible, waiting...")

        #     except pyautogui.ImageNotFoundException as e:
        #         # Image not found yet; continue waiting
        #         confidence_match = re.search(r'confidence = ([0-9.]+)', str(e))
        #         confidence = confidence_match.group(1) if confidence_match else "unknown"
        #         self.log(f"'Sprucing things up' window not yet visible (exception)), highest confidence: {confidence}, waiting...")

        #     except Exception as e:
        #         # Unexpected error; log and exit
        #         logging.error(f'Unexpected error: {e}')
        #         logging.error(traceback.format_exc())
        #         break

        #     time.sleep(1)  # Wait before next attempt

    def wait_for_teams_setup_to_complete(self):
        window_nickname = "Sprucing things up"
        self.log(f"Wating for window '{window_nickname}' to dissapear ...")
        hwnd = wait_for_window_to_disappear(self, window_title_substring="", window_class="EdgeUiInputTopWndClass" )

        if hwnd:
            self.log(f"Window '{window_nickname}' dissapeared. Continuing ...")
        else:
            self.log(f"Window '{window_nickname}' is still present.")


        # self.log(os.getcwd())
        # script_dir = os.path.abspath(os.path.dirname(__file__))
        # self.log(f"Script directory: {script_dir}")
        # image_path = os.path.join(os.path.dirname(__file__), "sprucing_things_up_window.png")
        # self.log(f"Image path: {image_path}")
        # self.log(f"Image exists: {os.path.exists(image_path)}")

        # while True:
        #     try:
        #         window_found = pyautogui.locateOnScreen(image_path, confidence=0.8)
        #         if window_found:
        #             self.log("'Sprucing things up' window still visible, waiting...")
        #         else:
        #             # This might not be reached if exception is thrown instead
        #             self.log("'Sprucing things up' windows dissapeared. Time to continue.")
        #             break

        #     except pyautogui.ImageNotFoundException:
        #         # Image not found; means window has disappeared
        #         confidence_match = re.search(r'confidence = ([0-9.]+)', str(e))
        #         confidence = confidence_match.group(1) if confidence_match else "unknown"
        #         self.log(f"'Sprucing things up' windows dissapeared (via exception), highest confidence: {confidence}. Time to continue.")
        #         break

        #     except Exception as e:
        #         # Unexpected error, log details
        #         logging.error(f'Unexpected error: {e}')
        #         logging.error(traceback.format_exc())
        #         break

        #     time.sleep(1)

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
        time.sleep(5)  # Wait for password entry field

        teams_config = tools_config.get("Microsoft Teams", {}).get("user", {})
        password = teams_config.get("password", "")

        if password:
            pyautogui.write(password)
            pyautogui.press("enter")
            self.log("Entered Teams password successfully.")
        else:
            self.log("No password found in software.json")

    def wait_for_all_set_window(self):
        self.log(os.getcwd())
        script_dir = os.path.abspath(os.path.dirname(__file__))
        self.log(f"Script directory: {script_dir}")
        image_path = os.path.join(os.path.dirname(__file__), "all_set.png")
        self.log(f"Image path: {image_path}")
        self.log(f"Image exists: {os.path.exists(image_path)}")

        while True:
            try:
                window_found = pyautogui.locateOnScreen(image_path, confidence=0.8)

                if window_found:
                    self.log("Teams 'All set' window appeared!")
                    break  # Image found; exit loop

                else:
                    self.log("'All set' window not yet visible, waiting...")

            except pyautogui.ImageNotFoundException:
                # Image not found yet; continue waiting
                confidence_match = re.search(r'confidence = ([0-9.]+)', str(e))
                confidence = confidence_match.group(1) if confidence_match else "unknown"
                self.log(f"'All set' window not yet visible (exception), highest confidence: {confidence}, waiting...")

            except Exception as e:
                # Unexpected error; log and exit
                logging.error(f'Unexpected error: {e}')
                logging.error(traceback.format_exc())
                break

            time.sleep(1)  # Wait before next attempt

    def configure_microsoft_teams(self, tools_config):
        self.log("Configuring Microsoft Teams...")

        try:
            self.log("Launching Microsoft Teams...")
            self.launch_teams()
            time.sleep(5)

            # Automate clicking "Finish Setup"
            self.log("Clicking 'Finish Setup'...")
            self.press_enter()

            self.log("Waiting for 'Sprucing things up' window to appear...")
            self.wait_for_teams_setup_window()

            # Wait for the next window to appear
            self.log("Waiting for 'Sprucing things up' window to complete...")
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
            time.sleep(10)

            # Click Enter to confirm
            self.press_enter()
            time.sleep(5)

            # Wait until "All set"
            self.log("Waiting for 'All set' window to appear...")
            self.wait_for_all_set_window()

            # Click Enter to confirm
            self.press_enter()
            time.sleep(5)

            self.log("Microsoft Teams configured successfully.")
        except Exception as e:
            self.log(f"Error configuring Teams: {e}")
            logging.error(f"Error configuring Teams: {e}")

