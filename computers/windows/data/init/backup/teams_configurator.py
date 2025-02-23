import os
import glob
import subprocess
import asyncio
import pyautogui
import logging
import traceback

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

    async def press_enter(self, delay=2):
        await asyncio.sleep(delay)
        pyautogui.press("enter")

    async def wait_for_teams_setup_to_complete(self, image_path, timeout=60):
        self.log("Waiting for Teams setup window to disappear...")
        try:
            for _ in range(timeout):
                window_found = pyautogui.locateOnScreen(image_path, confidence=0.8)
                if not window_found:
                    self.log("Teams setup completed.")
                    return
                await asyncio.sleep(1)
            self.log("Timeout waiting for Teams setup to complete.")
        except Exception as e:
            logging.error(f'Error: {e}')
            traceback_str = traceback.format_exc()
            logging.error(traceback_str)

    async def click_sign_in_button(self, image_path, timeout=30):
        self.log("Attempting to click 'Sign in' button...")
        try:
            for _ in range(timeout):
                button_location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
                if button_location:
                    pyautogui.moveTo(button_location, duration=1)
                    pyautogui.click()
                    self.log("Clicked 'Sign in' button successfully.")
                    return
                await asyncio.sleep(1)
            self.log("Error: Could not find 'Sign in' button on the screen.")
        except Exception as e:
            logging.error(f"Failed to interact with Teams sign-in screen: {e}")

    async def enter_text(self, text, delay=2):
        await asyncio.sleep(delay)
        pyautogui.write(text)
        pyautogui.press("enter")

    async def wait_for_all_set_window(self, image_path, timeout=30):
        for _ in range(timeout):
            window_found = pyautogui.locateOnScreen(image_path, confidence=0.8)
            if window_found:
                self.log("'All set' window detected!")
                return True
            await asyncio.sleep(1)
        self.log("Timeout: 'All set' window not found.")
        return False

    async def configure_microsoft_teams(self, tools_config, images):
        try:
            self.launch_teams()
            await self.press_enter(delay=5)
            await self.wait_for_teams_setup_to_complete(images["setup_complete"])
            await self.click_sign_in_button(images["sign_in_button"])
            await self.enter_text(tools_config.get("Microsoft Teams", {}).get("user", {}).get("name", ""))
            await self.enter_text(tools_config.get("Microsoft Teams", {}).get("user", {}).get("password", ""))
            await self.press_enter()
            await self.wait_for_all_set_window(images["all_set"])
            await self.press_enter()
            self.log("Microsoft Teams configured successfully.")
        except Exception as e:
            self.log(f"Error configuring Teams: {e}")
            logging.error(f"Error configuring Teams: {e}")
