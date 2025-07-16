@echo off
setlocal EnableDelayedExpansion

REM ---------------------------
REM 0) Set Username
REM ---------------------------
if "%~1"=="" (
    set "USERNAME=Docker"
) else (
    set "USERNAME=%~1"
)

echo Using username: %USERNAME%

if "%~2"=="" (
    set "DESTINATION=Docker"
) else (
    set "DESTINATION=%~2" 
)

echo Using destination: %DESTINATION%


REM ---------------------------
REM ---------------------------
REM ---------------------------
REM ---------------------------
REM 0.1) Setup log directory (outside C:\Data to prevent robocopy overwrite)
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

REM ---------------------------
REM 0.5) Copy all required files to C:\Data
REM ---------------------------
if /I "%DESTINATION%"=="Docker" (

    set "SOURCE=\\host.lan\Data"
    set "DEST=C:\Data"

    echo Ensuring %DEST% exists... >> "%LOGFILE%"
    if not exist "%DEST%" (
        mkdir "%DEST%"
        if %ERRORLEVEL% neq 0 (
            echo Failed to create %DEST% folder. >> "%LOGFILE%"
            exit /b %ERRORLEVEL%
        )
    )

    echo Copying data from %SOURCE% to %DEST%... >> "%LOGFILE%"
    robocopy "%SOURCE%" "%DEST%" /MIR /Z /NP /NFL /NDL /NJH /NJS /R:3 /W:5 >> "%LOGFILE%" 2>&1

    if %ERRORLEVEL% GEQ 8 (
        echo File copy failed with error code %ERRORLEVEL%. >> "%LOGFILE%"
        exit /b %ERRORLEVEL%
    )

    echo Files successfully copied to %DEST% >> "%LOGFILE%"
    
)

REM ---------------------------
REM ---------------------------
REM ---------------------------

echo Setting up winget links for PATH >> "%LOGFILE%"
setx PATH "%PATH%;%LOCALAPPDATA%\Microsoft\WinGet\Links" /M >nul

REM ---------------------------
REM 2) Download & Install Python system-wide (silent)
REM ---------------------------
set "PYTHON_INSTALLER=%TEMP%\python_installer.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"

REM Define Python paths
set "PYTHON_PATH=C:\Program Files\Python310\python.exe"
set "PYTHONW_PATH=C:\Program Files\Python310\pythonw.exe"

REM Check if Python is already installed
if exist %PYTHON_PATH% (
    echo Python is already installed at %PYTHON_PATH%. Skipping installation. >> "%LOGFILE%"
) else (
    echo Python not found. Proceeding with installation. >> "%LOGFILE%"
    
    echo Downloading Python installer... >> "%LOGFILE%"
    curl -L -o "%PYTHON_INSTALLER%" "%PYTHON_URL%" >> "%LOGFILE%" 2>&1

    echo Installing Python system-wide... >> "%LOGFILE%"
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 InstallLauncherAllUsers=1 >> "%LOGFILE%" 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Python installation failed with error code %ERRORLEVEL%. >> "%LOGFILE%"
        exit /b %ERRORLEVEL%
    )
)

setx PYTHON "%PYTHON_PATH%" /M >nul
setx PYTHONW "%PYTHONW_PATH%" /M >nul

echo Python set to %PYTHON_PATH% >> "%LOGFILE%"
echo Pythonw set to %PYTHONW_PATH% >> "%LOGFILE%"

REM ---------------------------
REM 3) Run Initialization Script
REM ---------------------------

REM Update pip
echo Updating pip... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install --upgrade pip >> "%LOGFILE%" 2>&1

REM Install Python libraries for INITIALIZE
echo Installing Python libraries for INITIALIZE... >> %LOGFILE%
"%PYTHON_PATH%" -m pip install -r "C:\Data\init\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for INITIALIZE installed successfully! >> %LOGFILE%

REM Run INITIALIZE Python script
echo Running Python script INITIALIZE ... >> %LOGFILE%
"%PYTHON_PATH%" "C:\Data\init\main.py" "%USERNAME%" >> "%LOGFILE%" 2>&1
echo Python script INITIALIZE executed. >> %LOGFILE%

REM ---------------------------
REM 4) Install Required Python Packages for SERVERS
REM ---------------------------
echo Installing Python libraries for 'server browser control' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\Data\server_browser_control\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server browser control' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'server network proxy' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\Data\server_network_proxy\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server network proxy' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'server evaluator' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\Data\server_evaluator\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server evaluator' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'server teams control' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\Data\server_teams_control\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server teams control' were installed >> "%LOGFILE%"

echo Installing Python libraries for 'server appium' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\Data\server_appium\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'server appium' were installed >> "%LOGFILE%"


echo Installing Python libraries for 'MCP Computer Control' ... >> "%LOGFILE%"
"%PYTHON_PATH%" -m pip install -r "C:\Data\mcp_computer_control\requirements.txt" >> "%LOGFILE%" 2>&1
echo Python libraries for 'MCP Computer Control' were installed >> "%LOGFILE%"


REM ---------------------------
REM 5) Add Firewall Rules
REM ---------------------------
echo Adding firewall rules... >> "%LOGFILE%"
netsh advfirewall firewall add rule name="SERVER_BROWSER_CONTROL" dir=in action=allow protocol=TCP localport=5051
netsh advfirewall firewall add rule name="SERVER_NETWORK_PROXY" dir=in action=allow protocol=TCP localport=5052
netsh advfirewall firewall add rule name="SERVER_EVALUATOR" dir=in action=allow protocol=TCP localport=5053
netsh advfirewall firewall add rule name="SERVER_TEAMS_CONTROL" dir=in action=allow protocol=TCP localport=5056
REM Add firewall rule for Appium (port 4723)
netsh advfirewall firewall add rule name="Appium" dir=in action=allow protocol=TCP localport=4723
REM Firewall rule for Playwright MCP is handled by its install script
REM Add firewall rule for MCP Computer Control (port 8003)
netsh advfirewall firewall add rule name="MCP_COMPUTER_CONTROL" dir=in action=allow protocol=TCP localport=8003
echo Firewall rules added >> "%LOGFILE%"

REM ---------------------------
REM 6) Create Startup Script
REM ---------------------------
echo Creating .bat files for servers >> "%LOGFILE%"
set "STARTUP_SERVER_BROWSER_CONTROL_BAT=%~dp0start_server_browser_control.bat"
(
    echo @echo off
    echo set LOGFILE=C:\Logs\BrowserControlServer-startup.txt
    echo call :logTime ^>^> %%LOGFILE%%
    echo start /b "BrowserControlServer" "%PYTHONW_PATH%" "C:\Data\server_browser_control\server.py"
    echo exit /b
    echo.
    echo :logTime
    echo setlocal ENABLEEXTENSIONS
    echo set "ts=%%date%% %%time%%"
    echo echo [%%ts%%] Triggered: BrowserControlServer
    echo exit /b
) > "%STARTUP_SERVER_BROWSER_CONTROL_BAT%"

set "STARTUP_SERVER_NETWORK_PROXY_BAT=%~dp0start_server_network_proxy.bat"
(
    echo @echo off
    echo set LOGFILE=C:\Logs\NetworkProxyServer-startup.txt
    echo call :logTime ^>^> %%LOGFILE%%
    echo start /b "NetworkProxyServer" "%PYTHONW_PATH%" "C:\Data\server_network_proxy\server.py"
    echo exit /b
    echo.
    echo :logTime
    echo setlocal ENABLEEXTENSIONS
    echo set "ts=%%date%% %%time%%"
    echo echo [%%ts%%] Triggered: NetworkProxyServer
    echo exit /b
) > "%STARTUP_SERVER_NETWORK_PROXY_BAT%"

set "STARTUP_SERVER_EVALUATOR_BAT=%~dp0start_server_evaluator.bat"
(
    echo @echo off
    echo set LOGFILE=C:\Logs\ServerEvaluatorServer-startup.txt
    echo call :logTime ^>^> %%LOGFILE%%
    echo start /b "ServerEvaluatorServer" "%PYTHONW_PATH%" "C:\Data\server_evaluator\server.py"
    echo exit /b
    echo.
    echo :logTime
    echo setlocal ENABLEEXTENSIONS
    echo set "ts=%%date%% %%time%%"
    echo echo [%%ts%%] Triggered: ServerEvaluatorServer
    echo exit /b
) > "%STARTUP_SERVER_EVALUATOR_BAT%"

set "STARTUP_SERVER_TEAMS_CONTROL_BAT=%~dp0start_server_teams_control.bat"
(
    echo @echo off
    echo set LOGFILE=C:\Logs\TeamsControlServer-startup.txt
    echo call :logTime ^>^> %%LOGFILE%%
    echo start /b "TeamsControlServer" "%PYTHONW_PATH%" "C:\Data\server_teams_control\server.py"
    echo exit /b
    echo.
    echo :logTime
    echo setlocal ENABLEEXTENSIONS
    echo set "ts=%%date%% %%time%%"
    echo echo [%%ts%%] Triggered: TeamsControlServer
    echo exit /b
) > "%STARTUP_SERVER_TEAMS_CONTROL_BAT%"

set "STARTUP_APPIUM_SERVER_BAT=%~dp0start_server_appium.bat"
(
    echo @echo off
    echo set LOGFILE=C:\Logs\AppiumServer-startup.txt
    echo call :logTime ^>^> %%LOGFILE%%
    echo start /b "AppiumServer" "%PYTHONW_PATH%" "C:\Data\server_appium\server.py" "%USERNAME%"
    echo exit /b
    echo.
    echo :logTime
    echo setlocal ENABLEEXTENSIONS
    echo set "ts=%%date%% %%time%%"
    echo echo [%%ts%%] Triggered: AppiumServer
    echo exit /b
) > "%STARTUP_APPIUM_SERVER_BAT%"


set "STARTUP_MCP_COMPUTER_CONTROL_BAT=%~dp0start_mcp_computer_control.bat"
(
    echo @echo off
    echo set LOGFILE=C:\Logs\MCPComputerControl-startup.txt
    echo call :logTime ^>^> %%LOGFILE%%
    echo start /b "MCPComputerControl" "%PYTHONW_PATH%" "C:\Data\mcp_computer_control\server.py"
    echo exit /b
    echo.
    echo :logTime
    echo setlocal ENABLEEXTENSIONS
    echo set "ts=%%date%% %%time%%"
    echo echo [%%ts%%] Triggered: MCPComputerControl
    echo exit /b
) > "%STARTUP_MCP_COMPUTER_CONTROL_BAT%"

echo .bat files for servers created >> "%LOGFILE%"

REM ---------------------------
REM 7) Enable Task Scheduler History
REM ---------------------------
echo Enabling Task Scheduler history >> "%LOGFILE%"
wevtutil set-log "Microsoft-Windows-TaskScheduler/Operational" /enabled:true >> "%LOGFILE%" 2>&1

REM ---------------------------
REM 8) Schedule Startup Task
REM ---------------------------
REM Without /IT, the task will not run interactively = will not be able to catch screenshots and record videos
REM Without /DELAY is needed in order to wait until network storage is available and user is logged in
echo Creating 'scheduled tasks' for servers >> "%LOGFILE%"
REM Logging
schtasks /Create /TN "Log-OnStartup" /SC ONLOGON /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"C:\OEM\on_startup.ps1\"" /RU "%USERNAME%" /RL HIGHEST /IT /F
REM OO Servers
schtasks /Create /TN "StartServer-BrowserControl" /SC ONLOGON /TR "\"%STARTUP_SERVER_BROWSER_CONTROL_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /F
schtasks /Create /TN "StartServer-NetworkProxy" /SC ONLOGON /TR "\"%STARTUP_SERVER_NETWORK_PROXY_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /F
schtasks /Create /TN "StartServer-Evaluator" /SC ONLOGON /TR "\"%STARTUP_SERVER_EVALUATOR_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /F
schtasks /Create /TN "StartServer-TeamsControl" /SC ONLOGON /TR "\"%STARTUP_SERVER_TEAMS_CONTROL_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /F
REM Appium
schtasks /Create /TN "StartServer-Appium" /SC ONLOGON /TR "\"%STARTUP_APPIUM_SERVER_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /F
REM MCP Playwright scheduled task is created by its install script
REM MCP Computer Control
schtasks /Create /TN "StartServer-MCPComputerControl" /SC ONLOGON /TR "\"%STARTUP_MCP_COMPUTER_CONTROL_BAT%\"" /RU "%USERNAME%" /RL HIGHEST /IT /F
echo 'Scheduled tasks' for servers created >> "%LOGFILE%"

echo Triggering 'scheduled tasks' for servers >> "%LOGFILE%"
REM Logging
schtasks /Run /TN "Log-OnStartup"
REM OO Servers
schtasks /Run /TN "StartServer-BrowserControl"
schtasks /Run /TN "StartServer-NetworkProxy"
schtasks /Run /TN "StartServer-Evaluator"
schtasks /Run /TN "StartServer-TeamsControl"
REM Appium
schtasks /Run /TN "StartServer-Appium"
REM MCP Playwright task is triggered by its install script
REM MCP Computer Control
schtasks /Run /TN "StartServer-MCPComputerControl"
echo 'Scheduled tasks' for servers started >> "%LOGFILE%"

echo Installation completed at %date% %time% >> "%LOGFILE%"
echo Installation complete. Servers will start automatically on reboot.
exit
