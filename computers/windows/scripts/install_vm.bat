@echo off
setlocal EnableDelayedExpansion

REM ---------------------------
REM 1) Set up logging
REM ---------------------------
set "LOGFILE=..\data\logs\install_bat.txt"
echo ================================================= >> "%LOGFILE%"
echo Installation started at %date% %time% >> "%LOGFILE%"
echo ================================================= >> "%LOGFILE%"

REM ---------------------------
REM 2) Download & Install Python system-wide (silent)
REM ---------------------------
set "PYTHON_INSTALLER=%TEMP%\python_installer.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"

echo Downloading Python installer... >> "%LOGFILE%"
curl -L -o "%PYTHON_INSTALLER%" "%PYTHON_URL%" >> "%LOGFILE%" 2>&1

echo Installing Python system-wide... >> "%LOGFILE%"
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 InstallLauncherAllUsers=1 >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python installation failed with error code %ERRORLEVEL%. >> "%LOGFILE%"
    exit /b %ERRORLEVEL%
)

set "PYTHON_PATH=C:\Program Files\Python310\python.exe"
set "PYTHONW_PATH=C:\Program Files\Python310\pythonw.exe"
setx PYTHON "%PYTHON_PATH%" /M >nul
setx PYTHONW "%PYTHONW_PATH%" /M >nul

echo Python set to %PYTHON_PATH% >> "%LOGFILE%"
echo Pythonw set to %PYTHONW_PATH% >> "%LOGFILE%"



REM ---------------------------
REM 3) Install software
REM ---------------------------

REM Update pip
"%PYTHON_PATH%" -m pip install --upgrade pip >> "%LOGFILE%" 2>&1

REM Install Python libraries for INITIALIZE
echo Installing Python libraries for INITIALIZE... >> %LOGFILE%
"%PYTHON_PATH%" -m pip install -r "..\data\init\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for INITIALIZE installed successfully! >> %LOGFILE%

REM Run INITIALIZE Python script from network path
echo Running Python script INITIALIZE from network... >> %LOGFILE%
"%PYTHON_PATH%" "..\data\init\main.py" >> "%LOGFILE%" 2>&1
echo Python script INITIALIZE executed. >> %LOGFILE%



REM ---------------------------
REM 4) Install Required Python Packages for SERVERS
REM ---------------------------
echo Installing Python libraries... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "..\data\server1\requirements.txt" >> "%LOGFILE%" 2>&1
"%PYTHON_PATH%" -m pip install -r "..\data\server2\requirements.txt" >> "%LOGFILE%" 2>&1

REM ---------------------------
REM 5) Add Firewall Rules
REM ---------------------------
echo Adding firewall rules... >> "%LOGFILE%"
netsh advfirewall firewall add rule name="SERVER1 Flask" dir=in action=allow protocol=TCP localport=6000
netsh advfirewall firewall add rule name="SERVER2 Flask" dir=in action=allow protocol=TCP localport=5000

REM ---------------------------
REM 6) Create Startup Script
REM ---------------------------
set "STARTUP_SERVER1_BAT=%~dp0start_server_1.bat"
(
    echo @echo off
    echo start /b "" "%PYTHONW_PATH%" "..\data\server1\main.py"
) > "%STARTUP_SERVER1_BAT%"

set "STARTUP_SERVER2_BAT=%~dp0start_server_2.bat"
(
    echo @echo off
    echo start /b "" "%PYTHONW_PATH%" "..\data\server2\main.py"
) > "%STARTUP_SERVER2_BAT%"

REM ---------------------------
REM 7) Schedule Startup Task
REM ---------------------------
REM Without /IT, the task will not run interactively = will not be able to catch screenshots and record videos
REM Without /DELAY is needed in order to wait until network storage is available and user is logged in
schtasks /Create /TN "StartServer1" /SC ONSTART /TR "\"%STARTUP_SERVER1_BAT%\"" /RU "Docker" /RL HIGHEST /IT /DELAY 0000:30 /F
schtasks /Create /TN "StartServer2" /SC ONSTART /TR "\"%STARTUP_SERVER2_BAT%\"" /RU "Docker" /RL HIGHEST /IT /DELAY 0000:30 /F
schtasks /Run /TN "StartServer1"
schtasks /Run /TN "StartServer2"

echo Installation completed at %date% %time% >> "%LOGFILE%"
echo Installation complete. Servers will start automatically on reboot.
exit
