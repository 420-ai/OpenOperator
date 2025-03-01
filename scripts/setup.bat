@echo off
echo Setting up monorepo project on Windows...

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python and try again.
    exit /b 1
)

:: Run the Python setup script
python setup.py

echo.
echo If setup.py ran successfully, you can activate the environment with:
echo .venv\Scripts\activate.bat