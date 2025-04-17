@echo off
setlocal EnableDelayedExpansion

REM ---------------------------
REM 0) Set Username
REM ---------------------------
if "%~1"=="" (
    set "USERNAME=lukaskellerstein"
) else (
    set "USERNAME=%~1"
)

echo Using username: %USERNAME%
echo Temp folder: %TEMP%
echo Current folder: %~dp0

REM ---------------------------
REM 1) Set up logging
REM ---------------------------
set "LOGDIR=C:\Logs"
set "LOGFILE=%LOGDIR%\install_bat.txt"

if not exist "%LOGDIR%" (
    mkdir "%LOGDIR%"
    if %ERRORLEVEL% neq 0 (
        echo Failed to create log folder at %LOGDIR%. Exiting.
        exit /b %ERRORLEVEL%
    )
)

echo ================================================= >> "%LOGFILE%"
echo Installation started at %date% %time% >> "%LOGFILE%"
echo ================================================= >> "%LOGFILE%"

echo Setting up winget links for PATH >> "%LOGFILE%"
setx PATH "%PATH%;%LOCALAPPDATA%\Microsoft\WinGet\Links" /M >nul

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
echo Updating pip... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install --upgrade pip >> "%LOGFILE%" 2>&1

REM Install Python libraries for INITIALIZE
echo Installing Python libraries for INITIALIZE... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\INSTALL\data\init\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for INITIALIZE installed successfully! >> "%LOGFILE%"

REM Run INITIALIZE Python script from network path
echo Running Python script INITIALIZE from network... >> "%LOGFILE%"
"%PYTHON_PATH%" "C:\INSTALL\data\init\main.py" "%USERNAME%" >> "%LOGFILE%" 2>&1
echo Python script INITIALIZE executed. >> "%LOGFILE%"

REM ---------------------------
REM 4) Install Required Python Packages for SERVERS
REM ---------------------------
echo Installing Python libraries for 'server computer control' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\INSTALL\data\server_computer_control\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server computer control' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'MCP server computer control' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\INSTALL\data\mcp_server_computer_control\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'MCP server computer control' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'server browser control' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\INSTALL\data\server_browser_control\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server browser control' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'server network proxy' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\INSTALL\data\server_network_proxy\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server network proxy' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'server evaluator' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\INSTALL\data\server_evaluator\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server evaluator' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'server teams control' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\INSTALL\data\server_teams_control\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server teams control' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'server appium' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\INSTALL\data\server_appium\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server appium' were installed >> "%LOGFILE%"


REM ---------------------------
REM 5) Add Firewall Rules
REM ---------------------------
echo Adding firewall rules... >> "%LOGFILE%"
REM Add firewall rule for OO Servers
netsh advfirewall firewall add rule name="SERVER_COMPUTER_CONTROL" dir=in action=allow protocol=TCP localport=5050
netsh advfirewall firewall add rule name="MCP_SERVER_COMPUTER_CONTROL" dir=in action=allow protocol=TCP localport=5055
netsh advfirewall firewall add rule name="SERVER_BROWSER_CONTROL" dir=in action=allow protocol=TCP localport=5051
netsh advfirewall firewall add rule name="SERVER_NETWORK_PROXY" dir=in action=allow protocol=TCP localport=5052
netsh advfirewall firewall add rule name="SERVER_EVALUATOR" dir=in action=allow protocol=TCP localport=5053
netsh advfirewall firewall add rule name="SERVER_TEAMS_CONTROL" dir=in action=allow protocol=TCP localport=5056
REM Add firewall rule for Chrome DevTools (port 9222)
netsh advfirewall firewall add rule name="Chrome Remote Debugging Port" dir=in action=allow protocol=TCP localport=9222
REM Add firewall rule for Appium (port 4723)
netsh advfirewall firewall add rule name="Appium" dir=in action=allow protocol=TCP localport=4723
echo Firewall rules added >> "%LOGFILE%"

REM ---------------------------
REM 6) Create Startup Script
REM ---------------------------
echo Creating .bat files for servers >> "%LOGFILE%"

REM OO Servers
set "STARTUP_SERVER_COMPUTER_CONTROL_BAT=%~dp0start_server_computer_control.bat"
(
    echo @echo off
    echo start /b "ComputerControlServer" "%PYTHONW_PATH%" "C:\INSTALL\data\server_computer_control\server.py"
) > "%STARTUP_SERVER_COMPUTER_CONTROL_BAT%"

set "STARTUP_MCP_SERVER_COMPUTER_CONTROL_BAT=%~dp0start_mcp_server_computer_control.bat"
(
    echo @echo off
    echo start /b "MCPComputerControlServer" "%PYTHONW_PATH%" "C:\INSTALL\data\mcp_server_computer_control\server.py"
) > "%STARTUP_MCP_SERVER_COMPUTER_CONTROL_BAT%"

set "STARTUP_SERVER_BROWSER_CONTROL_BAT=%~dp0start_server_browser_control.bat"
(
    echo @echo off
    echo start /b "BrowserControlServer" "%PYTHONW_PATH%" "C:\INSTALL\data\server_browser_control\server.py"
) > "%STARTUP_SERVER_BROWSER_CONTROL_BAT%"

set "STARTUP_SERVER_NETWORK_PROXY_BAT=%~dp0start_server_network_proxy.bat"
(
    echo @echo off
    echo start /b "NetworkProxyServer" "%PYTHONW_PATH%" "C:\INSTALL\data\server_network_proxy\server.py"
) > "%STARTUP_SERVER_NETWORK_PROXY_BAT%"

set "STARTUP_SERVER_EVALUATOR_BAT=%~dp0start_server_evaluator.bat"
(
    echo @echo off
    echo start /b "ServerEvaluatorServer" "%PYTHONW_PATH%" "C:\INSTALL\data\server_evaluator\server.py"
) > "%STARTUP_SERVER_EVALUATOR_BAT%"

set "STARTUP_SERVER_TEAMS_CONTROL_BAT=%~dp0start_server_teams_control.bat"
(
    echo @echo off
    echo start /b "TeamsControlServer" "%PYTHONW_PATH%" "C:\INSTALL\data\server_teams_control\server.py"
) > "%STARTUP_SERVER_TEAMS_CONTROL_BAT%"

set "STARTUP_APPIUM_SERVER_BAT=%~dp0start_server_appium.bat"
(
    echo @echo off
    echo start /b "AppiumServer" "%PYTHONW_PATH%" "C:\INSTALL\data\server_appium\server.py" "%USERNAME%"
) > "%STARTUP_APPIUM_SERVER_BAT%"

echo .bat files for servers created >> "%LOGFILE%"

REM ---------------------------
REM 7) Schedule Startup Task
REM ---------------------------
REM Without /IT, the task will not run interactively = will not be able to catch screenshots and record videos
REM Without /DELAY is needed in order to wait until network storage is available and user is logged in
echo Creating 'scheduled tasks' for servers >> "%LOGFILE%"
REM OO Servers
schtasks /Create /TN "StartServer-ComputerControl" /SC ONSTART /TR "\"%STARTUP_SERVER_COMPUTER_CONTROL_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /DELAY 0000:30 /F
schtasks /Create /TN "StartServer-MCPComputerControl" /SC ONSTART /TR "\"%STARTUP_MCP_SERVER_COMPUTER_CONTROL_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /DELAY 0000:30 /F
schtasks /Create /TN "StartServer-BrowserControl" /SC ONSTART /TR "\"%STARTUP_SERVER_BROWSER_CONTROL_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /DELAY 0000:30 /F
schtasks /Create /TN "StartServer-NetworkProxy" /SC ONSTART /TR "\"%STARTUP_SERVER_NETWORK_PROXY_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /DELAY 0000:30 /F
schtasks /Create /TN "StartServer-Evaluator" /SC ONSTART /TR "\"%STARTUP_SERVER_EVALUATOR_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /DELAY 0000:30 /F
schtasks /Create /TN "StartServer-TeamsControl" /SC ONSTART /TR "\"%STARTUP_SERVER_TEAMS_CONTROL_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /DELAY 0000:30 /F
REM Appium
schtasks /Create /TN "StartServer-Appium" /SC ONSTART /TR "\"%STARTUP_APPIUM_SERVER_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /DELAY 0000:30 /F
echo 'Scheduled tasks' for servers created >> "%LOGFILE%"

echo Triggering 'scheduled tasks' for servers >> "%LOGFILE%"
REM OO Servers
schtasks /Run /TN "StartServer-ComputerControl"
schtasks /Run /TN "StartServer-MCPComputerControl"
schtasks /Run /TN "StartServer-BrowserControl"
schtasks /Run /TN "StartServer-NetworkProxy"
schtasks /Run /TN "StartServer-Evaluator"
schtasks /Run /TN "StartServer-TeamsControl"
REM Appium
schtasks /Run /TN "StartServer-Appium"
echo 'Scheduled tasks' for servers started >> "%LOGFILE%"


echo Installation completed at %date% %time% >> "%LOGFILE%"
echo Installation complete. Servers will start automatically on reboot.
pause
