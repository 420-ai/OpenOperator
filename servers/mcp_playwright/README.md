# MCP Playwright Server

Official Playwright MCP server integration with two deployment options:
1. **Standard Mode** - Simple setup with minimized console (not fully working)
2. **CDP Mode** - Advanced setup with separate browser process (recommended)

## Features

- **Visible Browser** - See automation in action with browser window
- **Hidden Console** - Console window can be completely hidden (CDP mode)
- **Isolated Mode** - Each instance uses separate browser profile
- **Auto-start** - Runs on Windows login via Task Scheduler
- **CDP Support** - Connect to existing browser via Chrome DevTools Protocol

## CDP Mode (Recommended)

### How it Works

1. **Browser Process**: Launches Chrome/Edge with CDP debugging enabled (visible)
2. **MCP Server**: Connects to the browser via CDP endpoint (console hidden)
3. **Complete Separation**: Browser visibility is independent of MCP console

### Installation

Use `install_snippet_cdp.bat` instead of the standard installation:
```batch
call "C:\Data\mcp_playwright\install_snippet_cdp.bat" "%USERNAME%" "%LOGFILE%" "%~dp0"
```

### Architecture

1. Browser starts with `--remote-debugging-port=9222`
2. MCP server connects via `--cdp-endpoint http://localhost:9222`
3. Browser remains visible even when MCP console is hidden

## What install_snippet.bat Does

1. **Adds Firewall Rule** - Opens port 8931 for the Playwright MCP server
2. **Verifies Scripts** - Checks that startup scripts exist
3. **Creates Scheduled Task** - Sets up auto-start on user logon with interactive mode
4. **Starts the Server** - Triggers the task to start immediately

## Benefits

- **Modular Design** - All Playwright MCP logic is self-contained
- **Direct Official Server** - No Python wrapper overhead
- **Better Maintainability** - Updates don't require changing main install.bat
- **Proper Logging** - All output captured to dedicated log files

## Requirements

- **Administrator privileges** - Required for firewall rules (run install.bat as admin)
- **Node.js and npm** - Installed automatically via winget (OpenJS.NodeJS.LTS)
- **Internet connection** - For first run (npx will download the package)
- **Windows with Task Scheduler** - For auto-start functionality

## Node.js Path Resolution

The script automatically checks for npx.cmd in these locations:
1. `C:\Program Files\nodejs\npx.cmd`
2. `C:\Program Files (x86)\nodejs\npx.cmd`
3. `%LOCALAPPDATA%\Microsoft\WinGet\Links\npx.cmd`
4. Falls back to `npx` from PATH if not found

## Files

### Standard Mode
- `install_snippet.bat` - Standard installation script
- `start_playwright_powershell.ps1` - PowerShell script that runs the MCP server

### CDP Mode (Recommended)
- `install_snippet_cdp.bat` - CDP mode installation script
- `start_browser_cdp.bat` - Launches browser with CDP debugging
- `start_playwright_cdp.ps1` - Connects MCP to browser via CDP

### Documentation
- `README.md` - This documentation

## Server Details

- **Transport**: HTTP/SSE
- **MCP Port**: 8931
- **CDP Port**: 9222 (CDP mode only)
- **Standard Command**: `npx @playwright/mcp@latest --port 8931 --host 0.0.0.0 --output-dir ./output`
- **CDP Command**: `npx @playwright/mcp@latest --port 8931 --host 0.0.0.0 --output-dir ./output --cdp-endpoint http://localhost:9222`
- **Task Names**: 
  - Standard: `StartServer-MCPPlaywright`
  - CDP Browser: `StartBrowser-CDP`
  - CDP Server: `StartServer-MCPPlaywrightCDP`

## Troubleshooting

If the server doesn't start:
1. Check if Node.js is installed and in PATH
2. Run PowerShell directly to debug: `powershell -ExecutionPolicy Bypass -File C:\Data\mcp_playwright\start_playwright_powershell.ps1`
3. Check if the scheduled task exists: `schtasks /query /tn "StartServer-MCPPlaywright"`
4. Try running the task manually: `schtasks /run /tn "StartServer-MCPPlaywright"`
5. Check if port 8931 is in use: `netstat -an | findstr :8931`

### Common Issues

- **Browser not visible**: Ensure Task Scheduler task has `/IT` flag for interactive mode
- **"Browser already in use" error**: The `--isolated` flag should prevent this, but check for lingering processes
- **No Node.js process visible**: The server might be starting and immediately exiting. Check the log file
- **Port already in use**: Another process might be using port 8931
- **PATH not updated**: Node.js was installed but PATH wasn't refreshed in the current session

## Manual Testing

### Standard Mode
```bash
# Test via PowerShell with visible console
cd C:\Data\mcp_playwright
powershell -ExecutionPolicy Bypass -File start_playwright_powershell.ps1

# Test via scheduled task
schtasks /run /tn "StartServer-MCPPlaywright"
```

### CDP Mode (Recommended)
```bash
# Step 1: Start browser with CDP
cd C:\Data\mcp_playwright
start_browser_cdp.bat

# Step 2: In another console, start MCP server
powershell -ExecutionPolicy Bypass -File start_playwright_cdp.ps1

# Or use the convenience scripts:
start_mcp_cdp_all.bat  # Starts both browser and server
stop_mcp_cdp_all.bat   # Stops both

# Test via scheduled tasks
schtasks /run /tn "StartBrowser-CDP"
# Wait a few seconds
schtasks /run /tn "StartServer-MCPPlaywrightCDP"
```

### Verify CDP Connection
Open http://localhost:9222/json/version in your browser to verify CDP is working.