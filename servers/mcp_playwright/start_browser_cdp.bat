@echo off
REM Start Chrome/Edge with CDP debugging enabled for MCP Playwright connection
REM This browser will be visible and independent of MCP server console

echo Starting browser with CDP debugging on port 9222...

REM Check for Chrome first, then Edge
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_PATH=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
    set "BROWSER_NAME=Chrome"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_PATH=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
    set "BROWSER_NAME=Chrome"
) else if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_PATH=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
    set "BROWSER_NAME=Edge"
) else (
    echo ERROR: No Chrome or Edge browser found!
    echo Please install Chrome or Edge to use this feature.
    pause
    exit /b 1
)

echo Found %BROWSER_NAME% at: %BROWSER_PATH%

REM Kill any existing browser processes using port 9222
echo Checking for existing CDP sessions...
netstat -an | findstr :9222 >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Found existing CDP session on port 9222. Closing it...
    taskkill /F /IM chrome.exe >nul 2>&1
    taskkill /F /IM msedge.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

REM Create a dedicated user data directory for MCP
set "USER_DATA_DIR=%TEMP%\mcp-playwright-cdp-profile"
if not exist "%USER_DATA_DIR%" mkdir "%USER_DATA_DIR%"

echo Starting %BROWSER_NAME% with CDP debugging...
echo User data directory: %USER_DATA_DIR%
echo.

REM Start browser with CDP debugging
REM --remote-debugging-port=9222 enables CDP
REM --user-data-dir ensures clean profile
REM --no-first-run skips first run dialogs
REM --no-default-browser-check skips default browser prompt
start "" "%BROWSER_PATH%" ^
    --remote-debugging-port=9222 ^
    --user-data-dir="%USER_DATA_DIR%" ^
    --no-first-run ^
    --no-default-browser-check ^
    --disable-popup-blocking ^
    --disable-background-timer-throttling

echo.
echo Browser started with CDP debugging on port 9222
echo.
echo To verify CDP is working, open: http://localhost:9222/json/version
echo.
echo You can now run the MCP Playwright server with CDP connection.
echo The MCP console can be hidden while the browser remains visible.
echo.
pause