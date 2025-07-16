import os
import logging
from typing import Any
import shlex
import subprocess
import traceback

def execute_python_command(command: str):

    # print(command)
    # print(type(command))

    # data = command


    # # The 'command' key in the JSON request should contain the command to be executed.
    # shell = data.get('shell', False)
    # command = data.get('command', "" if shell else [])

    # if isinstance(command, str) and not shell:
    #     command = shlex.split(command)

    command = shlex.split(command)

    # Expand user directory
    for i, arg in enumerate(command):
        if arg.startswith("~/"):
            command[i] = os.path.expanduser(arg)

    # Execute the command without any safety checks.
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, text=True, timeout=120)
        return {
            'status': 'success',
            'output': result.stdout,
            'error': result.stderr,
            'returncode': result.returncode
        }
    except Exception as e:
        logging.error("\n" + traceback.format_exc() + "\n")
        return {
            'status': 'error',
            'message': str(e)
        }
