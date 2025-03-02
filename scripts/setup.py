#!/usr/bin/env python
"""
Cross-platform setup script for the monorepo project using uv sync.
Works on Windows, macOS, and Linux.
"""

import os
import subprocess
import sys
import platform

def run_command(command, shell=False):
    """Run a command and print its output."""
    print(f"Running: {' '.join(command) if isinstance(command, list) else command}")
    
    if shell:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    else:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    return process.poll()

def main():
    """Main setup function."""
    print(f"Setting up monorepo project on {platform.system()}...")
    
    # Check if uv is installed
    try:
        subprocess.run(["uv", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("UV is already installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing uv...")
        run_command([sys.executable, "-m", "pip", "install", "uv"])
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(".venv"):
        print("Creating virtual environment...")
        run_command(["uv", "venv"])
    else:
        print("Virtual environment already exists.")
    
    # Use uv sync to install all packages in the workspace
    print("Synchronizing workspace packages...")
    
    activate_cmd = ". .venv/bin/activate && "

    # Use different activation approach based on platform
    if platform.system() == "Windows":
        activate_cmd = r".venv\Scripts\activate.bat && "
        
    # Install dependencies
    run_command(f"{activate_cmd}uv sync", shell=True)

    run_command(f"{activate_cmd}uv pip install -r scripts/requirements-dev.txt", shell=True)

    # Test the CLI
    print("Testing CLI command...")
    run_command(f"{activate_cmd}ec hello", shell=True)
    
    print("\nSetup complete!")
    
    # Print usage instructions
    if platform.system() == "Windows":
        print("\nTo activate the environment, run:")
        print(r".venv\Scripts\activate.bat")
    else:
        print("\nTo activate the environment, run:")
        print(". .venv/bin/activate")
    
    print("\nAfter activation, you can use the CLI:")
    print("ec model download")

if __name__ == "__main__":
    main()