# MCP Computer Control Server

A Model Context Protocol (MCP) server that enables AI agents to control and interact with a computer through comprehensive automation tools.

## Features

### Core Computer Control Tools

#### Mouse Operations
- **mouse_move**: Move cursor to specified screen coordinates
- **mouse_scroll**: Scroll vertically/horizontally at current position or specified coordinates  
- **mouse_click**: Perform left/right/middle mouse click at current position or specified coordinates
- **mouse_double_click**: Perform double-click at current position or specified coordinates
- **mouse_drag**: Drag mouse from start position to end position

#### Keyboard Operations
- **keyboard_type**: Type text string with proper character encoding
- **keyboard_hotkeys**: Execute keyboard shortcuts (Ctrl+C, Alt+Tab, etc.)
- **keyboard_press**: Press a specific key multiple times

#### Screen Capture
- **take_screenshot**: Capture current screen state and return image data
- **get_screen_size**: Get current screen resolution
- **get_pixel_color**: Get the RGB color of a pixel at specified coordinates

### Extended Functionality Tools

#### File System Operations
- **download_file**: Download files from remote servers to specified local paths
- **list_files**: Get directory contents and file listings from specified paths
- **search_files**: Search for files by name/pattern within directory trees

#### System Information
- **get_system_info**: Retrieve OS, screen resolution, and system capabilities
- **get_active_window**: Get information about currently focused application/window
- **run_python_code**: Execute Python scripts on the local machine with output capture
- **show_notification**: Display system notifications or alerts

## Installation

1. Install dependencies:
```bash
cd servers/mcp_computer_control
uv sync
```

2. Run the server:
```bash
uv run python server.py
```

The server will be available at `http://0.0.0.0:8003/mcp`

## Dependencies

- **pyautogui**: Core mouse/keyboard automation
- **pillow**: Image processing for screenshots
- **pyqt6**: GUI framework for dialogs (optional)
- **requests**: HTTP downloads
- **psutil**: System information
- **mcp**: Model Context Protocol framework

## Security Features

- Input validation for all coordinate and text parameters
- Safe execution boundaries (timeouts, input validation)
- Screen resolution awareness
- Error handling for failed operations
- Cross-platform compatibility (Windows, macOS, Linux)

## Usage Examples

### Mouse Control
```python
# Move mouse to coordinates
{"tool": "mouse_move", "x": 100, "y": 200}

# Click at current position
{"tool": "mouse_click", "button": "left"}

# Drag from one point to another
{"tool": "mouse_drag", "start_x": 100, "start_y": 100, "end_x": 200, "end_y": 200}
```

### Keyboard Control
```python
# Type text
{"tool": "keyboard_type", "text": "Hello World!"}

# Execute hotkey
{"tool": "keyboard_hotkeys", "keys": "ctrl+c"}
```

### Screen Capture
```python
# Take full screenshot
{"tool": "take_screenshot"}

# Take screenshot of region
{"tool": "take_screenshot", "region": [0, 0, 800, 600]}
```

## Error Handling

All tools return structured JSON responses with success/error status:

```json
{
  "success": true,
  "position": {"x": 100, "y": 200},
  "screen_size": {"width": 1920, "height": 1080}
}
```

Failed operations return:
```json
{
  "success": false,
  "error": "Description of what went wrong"
}
```

## Platform Notes

### Linux
- May require `xdotool` for window management functions
- Install with: `sudo apt-get install xdotool`

### Windows  
- May require `pywin32` for advanced window operations
- Install with: `pip install pywin32`

### macOS
- May require `PyObjC` for window management
- Install with: `pip install PyObjC`