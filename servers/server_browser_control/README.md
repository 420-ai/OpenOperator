# Server Browser Control

HTTP API server for browser automation using Playwright. Now includes integrated MCP Playwright server management.

## Features

- **Browser Control**: Launch and control browsers via Playwright
- **CDP Support**: Chrome DevTools Protocol integration
- **MCP Integration**: Manage MCP Playwright server lifecycle
- **Remote Control**: All operations via HTTP API
- **Visible Browser**: Browser window is visible while MCP console is hidden

## Quick Start

```bash
# Start the server
python server.py

# Launch browser and MCP server
curl -X POST http://localhost:8910/launch-all

# Your MCP client can now connect to port 8931
# Browser is visible and controllable
```

# Endpoints

## ✅ **List of Exposed Functionalities (Endpoints):**

### Browser Control
| Method | Endpoint                     | Description                                 |
| ------ | ---------------------------- | ------------------------------------------- |
| GET    | `/healthcheck`               | Check service health status                 |
| POST   | `/browser/launch`            | Launch browser instance (with CDP port)     |
| POST   | `/browser/open`              | Open a URL in a new page                    |
| POST   | `/browser/close`             | Close browser instance                      |
| POST   | `/browser/cdp`               | Send Chrome DevTools Protocol (CDP) command |
| POST   | `/browser/screenshot`        | Take a screenshot of the specified page     |
| POST   | `/browser/get_cookies`       | Retrieve cookies for the specified page     |
| POST   | `/browser/start_tracing`     | Start browser tracing                       |
| POST   | `/browser/stop_tracing`      | Stop browser tracing                        |
| GET    | `/browser/download_trace`    | Download trace file                         |
| POST   | `/browser/get_local_storage` | Get local storage from specified page       |
| POST   | `/browser/execute_js`        | Execute JavaScript on specified page        |
| GET    | `/platform`                  | Get system platform info                    |
| GET    | `/cursor_position`           | Get current cursor position (x, y)          |

### MCP Playwright Integration (NEW)
| Method | Endpoint                     | Description                                 |
| ------ | ---------------------------- | ------------------------------------------- |
| POST   | `/mcp/start`                 | Start MCP Playwright server                 |
| POST   | `/mcp/stop`                  | Stop MCP Playwright server                  |
| GET    | `/mcp/status`                | Get MCP server status                       |
| POST   | `/mcp/restart`               | Restart MCP server                          |
| GET    | `/mcp/logs`                  | Get MCP server logs (placeholder)           |
| POST   | `/launch-all`                | Launch both browser and MCP server          |
| POST   | `/stop-all`                  | Stop both browser and MCP server            |
