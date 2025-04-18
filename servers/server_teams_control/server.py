from fastapi import FastAPI, Request, HTTPException
import logging
import time

import os
from logging_setup import configure_logging
from playwright.sync_api import sync_playwright
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.windows import WindowsOptions
from pydantic import BaseModel

from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Load environment variables from .env file
appium_url = os.getenv("APPIUM_URL")
teams_cdp_url = os.getenv("TEAMS_CDP_URL")

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logs_path = os.getenv("LOG_PATH")
logger = configure_logging(logs_path)
logger = logging.getLogger("server_teams_control")

# Port
port = os.getenv("PORT", 5056)


class SignInRequest(BaseModel):
    """Request model for sign-in."""

    username: str
    password: str

@app.post("/sign_in")
def sign_in(request: SignInRequest):
    """Endpoint to sign in to Teams."""
    logging.info("Sign-in request received.")

    try:
        with sync_playwright() as p:
            p.selectors.set_test_id_attribute("data-tid")

            # Connect to Teams webview2
            browser = p.chromium.connect_over_cdp(endpoint_url=teams_cdp_url)

            for ctx in browser.contexts:
                for page in ctx.pages:
                    url = urlparse(page.url)
                    if url.hostname.find("teams") > -1:
                        teams_ctx = ctx
                        break
                else:
                    continue  # Continue if the inner loop wasn't broken.
                break  # Inner loop was broken, break the outer.

            for page in teams_ctx.pages:
                viewport_contexts = page.locator('meta[name="viewportContext"]')
                if viewport_contexts.count() > 0:
                    teams_page = page

            # Connect to the Desktop Webdriver (Appium)
            windows_options = WindowsOptions()
            windows_options.app = "Root"

            appium = webdriver.Remote(
                command_executor=appium_url, options=windows_options
            )

            wait = WebDriverWait(appium, 60)

            teams_page.bring_to_front()

            appium.save_screenshot(os.path.join(logs_path, "01-teams_page.png"))    

            # Click on Sign In
            p.selectors.set_test_id_attribute("data-tid")
            teams_page.get_by_test_id("sign-in-button").or_(
                teams_page.get_by_test_id("another-account-button")
            ).click()

            teams_window = appium.find_element(
                AppiumBy.XPATH, "//Window[@Name='Microsoft Teams']"
            )

            teams_window.find_element(AppiumBy.XPATH, "//Pane").click()
            appium.save_screenshot(os.path.join(logs_path, "02-sign_in_desktop.png"))

            # Wait for the sign-in page to load
            sign_in_window = appium.find_element(
                AppiumBy.XPATH, '//Window[@Name="Sign in to Microsoft Teams"]'
            )
            sign_in_window.click()

            appium.save_screenshot(os.path.join(logs_path, "03-sign_in_email.png"))

            # email
            sign_in_window.find_element(
                AppiumBy.ACCESSIBILITY_ID, "emailTextInput"
            ).send_keys(request.username)

            # next
            sign_in_window.find_element(AppiumBy.ACCESSIBILITY_ID, "nextButton").click()

            # password
            appium.save_screenshot(os.path.join(logs_path, "04-sign_in_password.png"))

            password_input = wait.until(
                EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, "i0118"))
            )
            password_input.send_keys(request.password)

            appium.save_screenshot(os.path.join(logs_path, "05-sign_in_password.png"))

            appium.find_element(
                AppiumBy.XPATH,
                '//Button[@Name="Sign in" and @LocalizedControlType="button"]',
            ).click()

            appium.save_screenshot(os.path.join(logs_path, "06-sign_in_click.png"))

            # dismiss native post login prompt
            appium.find_element(
                AppiumBy.XPATH,
                '//*[@Name="No, sign in to this app only" and @LocalizedControlType="link"] | //*[@Name="Microsoft apps only" and @LocalizedControlType="link"] | //*[@Name="No, this app only" and @LocalizedControlType="button"]',
            ).click()

            appium.save_screenshot(os.path.join(logs_path, "07-sign_in_dismiss.png"))
            
    
    except Exception as e:
        import traceback

        logging.error(f"Sign-in error: {e}")
        error_traceback = traceback.format_exc()
        logging.error(error_traceback)
        return {"message": f"Sign-in unsuccessful: ${e}. Traceback: {error_traceback}"}

    return {"message": "Sign-in successful."}


@app.post("/configure")
async def configure_teams(request: Request):
    try:
        username = os.getlogin()

        # Read the JSON body
        json_data = await request.json()

        # Prepare config path
        teams_path = os.path.expandvars(fr"C:\Users\{username}\AppData\Local\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams")
        config_path = os.path.join(teams_path, "configuration.json")

        # Ensure the Teams path exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # Write the JSON to file
        with open(config_path, "w", encoding="utf-8") as f:
            import json
            json.dump(json_data, f, indent=2)

        return {"status": "success", "message": f"Configuration written to {config_path}"}

    except Exception as e:
        logger.error(f"Failed to configure Teams: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



if __name__ == "__main__":
    import uvicorn

    logging.info(f"Starting Teams Control server on port {port}...")

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(port),
            reload=False,
            log_config=None,  # Disable Uvicorn's default logging setup
        )
    except Exception as e:
        import traceback

        logging.error(f"Error starting server: {e}")
        error_traceback = traceback.format_exc()
        print(error_traceback)
