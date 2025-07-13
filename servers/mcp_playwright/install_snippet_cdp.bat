@echo off
REM MCP Playwright CDP Installation Script
REM This script sets up the CDP-based approach where browser runs separately

REM ---------------------------
REM Parameters from main install.bat
REM ---------------------------
set "USERNAME=%~1"
set "LOGFILE=%~2"
set "SCRIPTS_DIR=%~3"

if "%USERNAME%"=="" set "USERNAME=Lukas1234"
if "%LOGFILE%"=="" set "LOGFILE=C:\Logs\install_mcp_playwright_cdp.txt"
if "%SCRIPTS_DIR%"=="" set "SCRIPTS_DIR=%~dp0"

echo [MCP Playwright CDP] Starting installation... >> "%LOGFILE%"

REM ---------------------------
REM 1) Add Firewall Rules
REM ---------------------------
echo [MCP Playwright CDP] Adding firewall rules... >> "%LOGFILE%"
REM Port 8931 for MCP server
netsh advfirewall firewall add rule name="PLAYWRIGHT_MCP_OFFICIAL" dir=in action=allow protocol=TCP localport=8931 >> "%LOGFILE%" 2>&1
REM Port 9222 for Chrome DevTools Protocol
netsh advfirewall firewall add rule name="CHROME_CDP_DEBUG" dir=in action=allow protocol=TCP localport=9222 >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% neq 0 (
    echo [MCP Playwright CDP] WARNING: Failed to add firewall rules. Run as administrator. >> "%LOGFILE%"
)

REM ---------------------------
REM 2) Verify Scripts Exist
REM ---------------------------
echo [MCP Playwright CDP] Verifying scripts... >> "%LOGFILE%"
if not exist "C:\Data\mcp_playwright\start_browser_cdp.bat" (
    echo [MCP Playwright CDP] ERROR: start_browser_cdp.bat not found >> "%LOGFILE%"
    exit /b 1
)
if not exist "C:\Data\mcp_playwright\start_playwright_cdp.ps1" (
    echo [MCP Playwright CDP] ERROR: start_playwright_cdp.ps1 not found >> "%LOGFILE%"
    exit /b 1
)

REM ---------------------------
REM 3) Create Browser Startup Task
REM ---------------------------
echo [MCP Playwright CDP] Creating browser startup task... >> "%LOGFILE%"
REM Browser needs to be visible, so we use /IT flag
schtasks /Create /TN "StartBrowser-CDP" /SC ONLOGON /DELAY 0000:10 /TR "C:\Data\mcp_playwright\start_browser_cdp.bat" /RU "%USERNAME%" /RL HIGHEST /IT /F >> "%LOGFILE%" 2>&1

REM ---------------------------
REM 4) Create MCP Server Task
REM ---------------------------
echo [MCP Playwright CDP] Creating MCP server task... >> "%LOGFILE%"
REM MCP server can run hidden since browser is separate
REM Add extra delay to ensure browser starts first
schtasks /Create /TN "StartServer-MCPPlaywrightCDP" /SC ONLOGON /DELAY 0000:20 /TR "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File \"C:\Data\mcp_playwright\start_playwright_cdp.ps1\"" /RU "%USERNAME%" /RL HIGHEST /F >> "%LOGFILE%" 2>&1

REM ---------------------------
REM 5) Create Convenience Scripts
REM ---------------------------
echo [MCP Playwright CDP] Creating convenience scripts... >> "%LOGFILE%"

REM Create start_all.bat
echo @echo off > "%SCRIPTS_DIR%start_mcp_cdp_all.bat"
echo echo Starting CDP Browser and MCP Server... >> "%SCRIPTS_DIR%start_mcp_cdp_all.bat"
echo schtasks /Run /TN "StartBrowser-CDP" >> "%SCRIPTS_DIR%start_mcp_cdp_all.bat"
echo timeout /t 5 /nobreak ^>nul >> "%SCRIPTS_DIR%start_mcp_cdp_all.bat"
echo schtasks /Run /TN "StartServer-MCPPlaywrightCDP" >> "%SCRIPTS_DIR%start_mcp_cdp_all.bat"
echo echo Both services started. >> "%SCRIPTS_DIR%start_mcp_cdp_all.bat"

REM Create stop_all.bat
echo @echo off > "%SCRIPTS_DIR%stop_mcp_cdp_all.bat"
echo echo Stopping CDP Browser and MCP Server... >> "%SCRIPTS_DIR%stop_mcp_cdp_all.bat"
echo taskkill /F /IM chrome.exe 2^>nul >> "%SCRIPTS_DIR%stop_mcp_cdp_all.bat"
echo taskkill /F /IM msedge.exe 2^>nul >> "%SCRIPTS_DIR%stop_mcp_cdp_all.bat"
echo taskkill /F /IM node.exe /FI "WINDOWTITLE eq *playwright*" 2^>nul >> "%SCRIPTS_DIR%stop_mcp_cdp_all.bat"
echo echo Services stopped. >> "%SCRIPTS_DIR%stop_mcp_cdp_all.bat"

echo [MCP Playwright CDP] Installation completed >> "%LOGFILE%"
echo [MCP Playwright CDP] Browser will start on next login >> "%LOGFILE%"
echo [MCP Playwright CDP] MCP server will connect to browser via CDP >> "%LOGFILE%"
echo [MCP Playwright CDP] To start now: Run start_mcp_cdp_all.bat >> "%LOGFILE%"
exit /b 0