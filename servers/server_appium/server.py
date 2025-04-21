import subprocess
import time
import sys
import os
from dotenv import load_dotenv
load_dotenv()

LOG_PATH = os.getenv("LOG_PATH")
print(f"Logs path: {LOG_PATH}")

PORT = os.getenv("PORT")
print(f"Port: {PORT}")

def main():
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "docker"

    node_path = r"C:\Program Files\nodejs\node.exe"
    appium_js = fr"C:\Users\{username}\AppData\Roaming\npm\node_modules\appium\build\lib\main.js"

    args = [
        node_path,
        appium_js,
        '-p', f'{PORT}',
        # '--log', rf'{LOG_PATH}\AppiumServer.log'
    ]

    log_file_path = fr"{LOG_PATH}\appium_output.log"
    log_file = open(log_file_path, "w")

    DETACHED = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS

    process = subprocess.Popen(
        args,
        stdout=log_file,
        stderr=log_file,
        stdin=subprocess.DEVNULL,
        creationflags=DETACHED,
        close_fds=True
    )

    print(f"Appium started with PID: {process.pid}")
    log_file.close()

if __name__ == "__main__":
    main()
