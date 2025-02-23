@echo off

REM Set script directory
set SCRIPT_DIR=%~dp0

REM Log file path
set LOGFILE=%USERPROFILE%\Desktop\install_log.txt

REM Start logging
echo INSTALLATION STARTED AT %date% %time% > %LOGFILE%

REM ==========================================
REM Section 1: Initial Setup and Python Install
REM ==========================================

REM Download Python installer
echo Downloading Python... >> %LOGFILE%
curl -L -o "%TEMP%\python_installer.exe" "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe" >> %LOGFILE% 2>&1

REM Install Python silently
echo Installing Python... >> %LOGFILE%
"%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 >> %LOGFILE% 2>&1
echo Python installed successfully! >> %LOGFILE%

REM Define Python path
set PYTHON=%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe
echo Python path is set to %PYTHON% >> %LOGFILE%

@REM REM ==========================================
@REM REM Section 2: Install software
@REM REM ==========================================

@REM REM Install Python libraries for INITIALIZE
@REM echo Installing Python libraries for INITIALIZE... >> %LOGFILE%
@REM %PYTHON% -m pip install --upgrade pip >> %LOGFILE% 2>&1
@REM %PYTHON% -m pip install -r "\\host.lan\Data\init\requirements.txt" >> %LOGFILE% 2>&1
@REM echo Python libraries for INITIALIZE installed successfully! >> %LOGFILE%

@REM REM Run INITIALIZE Python script from network path
@REM echo Running Python script INITIALIZE from network... >> %LOGFILE%
@REM %PYTHON% "\\host.lan\Data\init\main.py" >> %LOGFILE% 2>&1
@REM echo Python script INITIALIZE executed. >> %LOGFILE%

@REM REM ==========================================
@REM REM Section 3: Setup for SERVER1
@REM REM ==========================================

@REM REM Make exception for Server1 in Windows Firewall
@REM netsh advfirewall firewall add rule name="SERVER1 Flask" dir=in action=allow protocol=TCP localport=6000

@REM REM Install Python libraries for SERVER1
@REM echo Installing Python libraries for SERVER1... >> %LOGFILE%
@REM %PYTHON% -m pip install --upgrade pip >> %LOGFILE% 2>&1
@REM %PYTHON% -m pip install -r "\\host.lan\Data\server1\requirements.txt" >> %LOGFILE% 2>&1
@REM echo Python libraries for SERVER1 installed successfully! >> %LOGFILE%

@REM REM Create scheduled task to run SERVER1 on startup (hidden)
@REM echo Creating scheduled task for SERVER1... >> %LOGFILE%
@REM schtasks /Create /TN "StartSERVER1" /TR "powershell -ExecutionPolicy Bypass -File \"%SCRIPT_DIR%run_server1.ps1\"" /SC ONLOGON /RL HIGHEST /F
@REM schtasks /Run /TN "StartSERVER1"
@REM echo Scheduled task for SERVER1 created successfully! >> %LOGFILE%

@REM REM Start SERVER1 immediately in the background (hidden)
@REM echo Starting SERVER1 immediately... >> %LOGFILE%
@REM powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run_server1.ps1"
@REM echo SERVER1 started. >> %LOGFILE%

@REM REM ==========================================
@REM REM Section 4: Setup for SERVER2
@REM REM ==========================================

@REM REM Make exception for Server1 in Windows Firewall
@REM netsh advfirewall firewall add rule name="SERVER2 Flask" dir=in action=allow protocol=TCP localport=5000

@REM REM Install Python libraries for SERVER2
@REM echo Installing Python libraries for SERVER2... >> %LOGFILE%
@REM %PYTHON% -m pip install --upgrade pip >> %LOGFILE% 2>&1
@REM %PYTHON% -m pip install -r "\\host.lan\Data\server2\requirements.txt" >> %LOGFILE% 2>&1
@REM echo Python libraries for SERVER2 installed successfully! >> %LOGFILE%

@REM REM Create scheduled task to run SERVER2 on startup (hidden)
@REM echo Creating scheduled task for SERVER2... >> %LOGFILE%
@REM schtasks /Create /TN "StartSERVER2" /TR "powershell -ExecutionPolicy Bypass -File \"%SCRIPT_DIR%run_server2.ps1\"" /SC ONLOGON /RL HIGHEST /F
@REM schtasks /Run /TN "StartSERVER2"
@REM echo Scheduled task for SERVER2 created successfully! >> %LOGFILE%

@REM REM Start SERVER2 immediately in the background (hidden)
@REM echo Starting SERVER2 immediately... >> %LOGFILE%
@REM powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run_server2.ps1"
@REM echo SERVER2 started. >> %LOGFILE%

REM ==========================================
REM Section 4: Setup for SERVER2
REM ==========================================

@REM REM Install Python libraries for SERVER2
@REM echo Installing Python libraries for SERVER2... >> %LOGFILE%
@REM %PYTHON% -m pip install --upgrade pip >> %LOGFILE% 2>&1
@REM %PYTHON% -m pip install -r "\\host.lan\Data\server2\requirements.txt" >> %LOGFILE% 2>&1
@REM echo Python libraries for SERVER2 installed successfully! >> %LOGFILE%

@REM REM Create scheduled task to run SERVER2 on startup
@REM echo Creating scheduled task for SERVER2... >> %LOGFILE%
@REM schtasks /Create /TN "StartSERVER2" /TR "%PYTHON% \\host.lan\Data\server2\main.py" /SC ONSTART /RL HIGHEST /F >> %LOGFILE% 2>&1
@REM echo Scheduled task for SERVER2 created successfully! >> %LOGFILE%

@REM REM Start SERVER2 immediately
@REM echo Starting SERVER2 immediately... >> %LOGFILE%
@REM start /B %PYTHON% -u "\\host.lan\Data\server1\main.py"
@REM echo SERVER2 started. >> %LOGFILE%

REM ==========================================
REM Installation Complete
REM ==========================================
echo INSTALLATION COMPLETED AT %date% %time% >> %LOGFILE%
