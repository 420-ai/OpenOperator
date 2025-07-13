# CDP Mode Setup Guide

## Overview

CDP (Chrome DevTools Protocol) mode solves the browser visibility problem by completely separating the browser process from the MCP server process. This allows the browser to be visible while the MCP server console remains hidden.

## How It Works

```
┌─────────────────────┐         ┌─────────────────────┐
│   Browser Process   │         │  MCP Server Process │
│  (Visible Window)   │◄────────│  (Hidden Console)   │
│                     │   CDP    │                     │
│ Port 9222 (Debug)   │         │  Port 8931 (MCP)    │
└─────────────────────┘         └─────────────────────┘
```

## Quick Start

1. **Install CDP Mode**:
   ```batch
   cd C:\Data\mcp_playwright
   install_snippet_cdp.bat
   ```

2. **Start Services**:
   ```batch
   start_mcp_cdp_all.bat
   ```

3. **Test Connection**:
   - Browser: Should be visible with a blank tab
   - CDP: http://localhost:9222/json/version
   - MCP: Your MCP client should connect to port 8931

## Manual Setup

### Step 1: Launch Browser with CDP
```batch
# Chrome
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\mcp-cdp"

# Edge
"C:\Program Files\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\mcp-cdp"
```

### Step 2: Start MCP Server
```bash
npx @playwright/mcp@latest --port 8931 --cdp-endpoint http://localhost:9222
```

## Benefits

1. **Complete Separation**: Browser and server are independent processes
2. **Full Visibility Control**: Browser always visible, console can be hidden
3. **Reusable Sessions**: Can reconnect to existing browser sessions
4. **Better Debugging**: Can inspect browser state via DevTools

## Troubleshooting

### Browser won't start
- Check if port 9222 is already in use: `netstat -an | findstr :9222`
- Kill existing Chrome/Edge processes and try again

### MCP can't connect to browser
- Ensure browser started with `--remote-debugging-port=9222`
- Check firewall allows port 9222
- Verify CDP endpoint: http://localhost:9222/json/version

### Multiple browser windows
- Each CDP session needs a unique port
- Use different ports: 9222, 9223, 9224, etc.

## Advanced Usage

### Custom CDP Port
```batch
# In start_browser_cdp.bat, change:
--remote-debugging-port=9223

# In start_playwright_cdp.ps1, change:
--cdp-endpoint http://localhost:9223
```

### Persistent Browser Profile
```batch
# Use a fixed directory instead of %TEMP%
--user-data-dir="C:\Data\mcp-browser-profile"
```

### Connect to Remote Browser
```bash
# If browser is on another machine
--cdp-endpoint http://192.168.1.100:9222
```