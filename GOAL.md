# Computer Control MCP Server - Project Goal

## Overview

Create a Model Context Protocol (MCP) server that enables AI agents to control and interact with a computer through a comprehensive set of automation tools. The server should use Streamable HTTP transport (following the pattern in `samples/mcp_http/my_server`).

## Core Computer Control Tools (Required)

The MCP server must implement the following essential computer control capabilities:

### Mouse Operations

- **mouse_move**: Move cursor to specified screen coordinates
- **mouse_scroll**: Scroll vertically/horizontally at current position or specified coordinates
- **mouse_left_click**: Perform left mouse click at current position or specified coordinates
- **mouse_double_click**: Perform double-click at current position or specified coordinates

### Keyboard Operations

- **keyboard_type**: Type text string with proper character encoding
- **keyboard_hotkeys**: Execute keyboard shortcuts (Ctrl+C, Alt+Tab, etc.)

### Screen Capture

- **take_screenshot**: Capture current screen state and return image data

## Extended Functionality Tools (Recommended)

Consider implementing these additional capabilities to enhance computer control:

### Code Execution

- **run_python_code**: Execute Python scripts on the local machine with output capture

### File System Operations

- **download_file**: Download files from remote servers to specified local paths
- **list_files**: Get directory contents and file listings from specified paths
- **search_files**: Search for files by name/pattern within directory trees

### User Interface

- **show_ui_dialog**: Display interactive dialogs, forms, or pop-ups using GUI framework (PyQt6 suggested)
- **show_notification**: Display system notifications or alerts
- **prompt_user**: Show input dialogs for user interaction

### System Information

- **get_system_info**: Retrieve OS, screen resolution, and system capabilities
- **get_active_window**: Get information about currently focused application/window

## Technical Implementation Guidelines

### Recommended Technology Stack

- **Primary Library**: PyAutoGUI for core mouse/keyboard automation
- **Alternative Options**: Consider pynput, keyboard, or platform-specific libraries if needed
- **GUI Framework**: PyQt6 for dialog/UI components
- **HTTP Transport**: Follow existing MCP HTTP server patterns

### Key Requirements

- Cross-platform compatibility (Windows, macOS, Linux where possible)
- Error handling for failed operations (screen locked, permissions, etc.)
- Coordinate system handling (screen resolution awareness)
- Safe execution boundaries (prevent infinite loops, validate inputs)
- Proper image encoding for screenshot data transfer

### Security Considerations

- Input validation for all coordinate and text parameters
- Rate limiting for rapid-fire operations
- Safe file path handling for file operations
- Execution timeouts for long-running operations

## Success Criteria

The completed MCP server should enable an AI agent to:

1. Navigate and interact with any desktop application through mouse/keyboard
2. Capture and analyze screen content through screenshots
3. Perform file management and system interaction tasks
4. Display custom interfaces for user interaction when needed
5. Execute automation scripts and workflows reliably

## Project Structure

Follow MCP HTTP server conventions with proper tool registration, parameter validation, and response formatting. Ensure all tools are properly documented with clear parameter specifications and return value formats.
