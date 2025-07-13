# PowerShell script to start Playwright MCP server with CDP connection
# This connects to an already-running browser, so console can be hidden

# Set working directory
Set-Location "C:\Data"

# Path to npx
$npxPath = if (Test-Path "C:\Program Files\nodejs\npx.cmd") {
    "C:\Program Files\nodejs\npx.cmd"
} elseif (Test-Path "C:\Program Files (x86)\nodejs\npx.cmd") {
    "C:\Program Files (x86)\nodejs\npx.cmd"
} elseif (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Links\npx.cmd") {
    "$env:LOCALAPPDATA\Microsoft\WinGet\Links\npx.cmd"
} else {
    "npx"
}

# Check if CDP endpoint is accessible
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9222/json/version" -UseBasicParsing -TimeoutSec 2
    Write-Host "CDP endpoint is accessible. Browser is ready." -ForegroundColor Green
} catch {
    Write-Host "WARNING: Cannot connect to CDP endpoint at http://localhost:9222" -ForegroundColor Yellow
    Write-Host "Please ensure browser is running with --remote-debugging-port=9222" -ForegroundColor Yellow
    Write-Host "Run start_browser_cdp.bat first to launch the browser." -ForegroundColor Yellow
}

# Start the Playwright MCP server with CDP connection
Write-Host "Starting Playwright MCP server with CDP connection..." -ForegroundColor Cyan
& $npxPath @playwright/mcp@latest --port 8931 --host 0.0.0.0 --output-dir ./output --cdp-endpoint http://localhost:9222