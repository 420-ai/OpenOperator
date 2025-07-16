import json
import uvicorn
from pydantic import AnyUrl
import os
import sys
import contextlib
from collections.abc import AsyncIterator
import logging
from logging_setup import configure_logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MCP
from mcp.server.lowlevel import Server
import mcp.types as types
from mcp.server.lowlevel.helper_types import ReadResourceContents

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

# Tool imports
from tools.mouse_operations import (
    mouse_move,
    mouse_scroll,
    mouse_left_click,
    mouse_double_click,
    mouse_right_click,
    mouse_drag,
)
from tools.keyboard_operations import (
    keyboard_type,
    keyboard_hotkeys,
    keyboard_press,
    keyboard_hold,
)
from tools.screen_operations import (
    take_screenshot,
    take_screenshot_with_cursor,
    get_screen_size,
    get_pixel_color,
    locate_image_on_screen,
)
from tools.file_operations import (
    download_file,
    list_files,
    search_files,
    create_directory,
    delete_file,
)
from tools.system_operations import (
    get_system_info,
    get_active_window,
    run_python_code,
    show_notification,
)
from tools.screen_recording import (
    start_recording,
    end_recording,
    get_recording,
    list_recordings,
)
from tools.window_operations import (
    launch_application,
    maximize_window,
    list_windows,
)


def serve():

    # Port
    port = os.getenv("PORT", 5040)
    print("PORT", port)
    port = int(port)  # Convert to integer

    # Configure logging
    logs_path = os.getenv("LOG_PATH", "C:\\Logs")
    configure_logging(logs_path)
    logger = logging.getLogger("mcp_computer_control")

    logger.info("Starting MCP Computer Control Server...")

    server = Server("mcp-computer-control")

    # ----------------------------------
    # Tools
    # ----------------------------------

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            # Mouse operations
            types.Tool(
                name="mouse_move",
                description="Move mouse cursor to specified screen coordinates",
                inputSchema={
                    "type": "object",
                    "required": ["x", "y"],
                    "properties": {
                        "x": {
                            "type": "integer",
                            "description": "X coordinate on screen",
                        },
                        "y": {
                            "type": "integer",
                            "description": "Y coordinate on screen",
                        },
                        "duration": {
                            "type": "number",
                            "description": "Movement duration in seconds",
                            "default": 0.5,
                        },
                    },
                },
            ),
            types.Tool(
                name="mouse_scroll",
                description="Scroll vertically/horizontally at current position or specified coordinates",
                inputSchema={
                    "type": "object",
                    "required": ["direction"],
                    "properties": {
                        "direction": {
                            "type": "string",
                            "enum": [
                                "up",
                                "down",
                                "left",
                                "right",
                                "vertical_up",
                                "horizontal_left",
                                "horizontal_right",
                            ],
                            "description": "Scroll direction",
                        },
                        "clicks": {
                            "type": "integer",
                            "description": "Number of scroll clicks",
                            "default": 3,
                        },
                        "x": {
                            "type": "integer",
                            "description": "X coordinate (optional)",
                        },
                        "y": {
                            "type": "integer",
                            "description": "Y coordinate (optional)",
                        },
                    },
                },
            ),
            types.Tool(
                name="mouse_click",
                description="Perform mouse click at current position or specified coordinates",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "integer",
                            "description": "X coordinate (optional)",
                        },
                        "y": {
                            "type": "integer",
                            "description": "Y coordinate (optional)",
                        },
                        "button": {
                            "type": "string",
                            "enum": ["left", "right", "middle"],
                            "default": "left",
                        },
                    },
                },
            ),
            types.Tool(
                name="mouse_double_click",
                description="Perform double-click at current position or specified coordinates",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "integer",
                            "description": "X coordinate (optional)",
                        },
                        "y": {
                            "type": "integer",
                            "description": "Y coordinate (optional)",
                        },
                        "button": {
                            "type": "string",
                            "enum": ["left", "right", "middle"],
                            "default": "left",
                        },
                    },
                },
            ),
            types.Tool(
                name="mouse_drag",
                description="Drag mouse from start position to end position",
                inputSchema={
                    "type": "object",
                    "required": ["start_x", "start_y", "end_x", "end_y"],
                    "properties": {
                        "start_x": {
                            "type": "integer",
                            "description": "Start X coordinate",
                        },
                        "start_y": {
                            "type": "integer",
                            "description": "Start Y coordinate",
                        },
                        "end_x": {"type": "integer", "description": "End X coordinate"},
                        "end_y": {"type": "integer", "description": "End Y coordinate"},
                        "duration": {
                            "type": "number",
                            "description": "Drag duration in seconds",
                            "default": 1.0,
                        },
                        "button": {
                            "type": "string",
                            "enum": ["left", "right", "middle"],
                            "default": "left",
                        },
                    },
                },
            ),
            # Keyboard operations
            types.Tool(
                name="keyboard_type",
                description="Type text string with proper character encoding",
                inputSchema={
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                        "text": {"type": "string", "description": "Text to type"},
                        "interval": {
                            "type": "number",
                            "description": "Interval between characters in seconds",
                            "default": 0.01,
                        },
                    },
                },
            ),
            types.Tool(
                name="keyboard_hotkeys",
                description="Execute keyboard shortcuts (Ctrl+C, Alt+Tab, etc.)",
                inputSchema={
                    "type": "object",
                    "required": ["keys"],
                    "properties": {
                        "keys": {
                            "oneOf": [
                                {
                                    "type": "string",
                                    "description": "Keyboard shortcut (e.g., 'ctrl+c', 'alt+tab')",
                                },
                                {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Array of keys",
                                },
                            ]
                        },
                        "interval": {
                            "type": "number",
                            "description": "Pause after execution",
                            "default": 0.1,
                        },
                    },
                },
            ),
            types.Tool(
                name="keyboard_press",
                description="Press a specific key multiple times",
                inputSchema={
                    "type": "object",
                    "required": ["key"],
                    "properties": {
                        "key": {"type": "string", "description": "Key to press"},
                        "presses": {
                            "type": "integer",
                            "description": "Number of times to press",
                            "default": 1,
                        },
                        "interval": {
                            "type": "number",
                            "description": "Interval between presses",
                            "default": 0.1,
                        },
                    },
                },
            ),
            # Screen operations
            types.Tool(
                name="take_screenshot",
                description="Capture current screen state and return image data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "minItems": 4,
                            "maxItems": 4,
                            "description": "Region to capture [x, y, width, height] (optional)",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["PNG", "JPEG"],
                            "default": "PNG",
                        },
                        "quality": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 95,
                        },
                    },
                },
            ),
            types.Tool(
                name="get_screen_size",
                description="Get current screen resolution",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="get_pixel_color",
                description="Get the RGB color of a pixel at specified coordinates",
                inputSchema={
                    "type": "object",
                    "required": ["x", "y"],
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate"},
                        "y": {"type": "integer", "description": "Y coordinate"},
                    },
                },
            ),
            types.Tool(
                name="take_screenshot_with_cursor",
                description="Capture screen with mouse cursor visible",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "minItems": 4,
                            "maxItems": 4,
                            "description": "Region to capture [x, y, width, height] (optional)",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["PNG", "JPEG"],
                            "default": "PNG",
                        },
                        "quality": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 95,
                        },
                    },
                },
            ),
            # Screen recording operations
            types.Tool(
                name="start_recording",
                description="Start recording the screen",
                inputSchema={
                    "type": "object",
                    "required": ["filename"],
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name for the recording (without extension)",
                        },
                    },
                },
            ),
            types.Tool(
                name="end_recording",
                description="End an active screen recording",
                inputSchema={
                    "type": "object",
                    "required": ["filename"],
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the recording to stop",
                        },
                    },
                },
            ),
            types.Tool(
                name="get_recording",
                description="Retrieve a recorded video file",
                inputSchema={
                    "type": "object",
                    "required": ["filename"],
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the recording to retrieve",
                        },
                    },
                },
            ),
            # Window operations
            types.Tool(
                name="launch_application",
                description="Launch applications or execute commands",
                inputSchema={
                    "type": "object",
                    "required": ["command"],
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Application name or command to execute",
                        },
                        "shell": {
                            "type": "boolean",
                            "description": "Execute in shell mode",
                            "default": False,
                        },
                    },
                },
            ),
            types.Tool(
                name="maximize_window",
                description="Maximize a window by title search",
                inputSchema={
                    "type": "object",
                    "required": ["title_contains"],
                    "properties": {
                        "title_contains": {
                            "type": "string",
                            "description": "Text to search for in window titles",
                        },
                    },
                },
            ),
            # File operations
            types.Tool(
                name="download_file",
                description="Download files from remote servers to specified local paths",
                inputSchema={
                    "type": "object",
                    "required": ["url", "local_path"],
                    "properties": {
                        "url": {
                            "type": "string",
                            "format": "uri",
                            "description": "URL to download from",
                        },
                        "local_path": {
                            "type": "string",
                            "description": "Local path to save file",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Request timeout in seconds",
                            "default": 30,
                        },
                    },
                },
            ),
            types.Tool(
                name="list_files",
                description="Get directory contents and file listings",
                inputSchema={
                    "type": "object",
                    "required": ["directory_path"],
                    "properties": {
                        "directory_path": {
                            "type": "string",
                            "description": "Directory path to list",
                        },
                        "pattern": {
                            "type": "string",
                            "description": "File pattern to match",
                            "default": "*",
                        },
                        "include_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files",
                            "default": False,
                        },
                    },
                },
            ),
            types.Tool(
                name="search_files",
                description="Search for files by name/pattern within directory trees",
                inputSchema={
                    "type": "object",
                    "required": ["directory_path", "filename_pattern"],
                    "properties": {
                        "directory_path": {
                            "type": "string",
                            "description": "Directory to search in",
                        },
                        "filename_pattern": {
                            "type": "string",
                            "description": "Filename pattern to search for",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Search recursively",
                            "default": True,
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum results",
                            "default": 100,
                        },
                    },
                },
            ),
            # System operations
            types.Tool(
                name="get_system_info",
                description="Retrieve OS, screen resolution, and system capabilities",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="get_active_window",
                description="Get information about currently focused application/window",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="run_python_code",
                description="Execute Python scripts with output capture",
                inputSchema={
                    "type": "object",
                    "required": ["code"],
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Execution timeout in seconds",
                            "default": 30,
                        },
                    },
                },
            ),
            types.Tool(
                name="show_notification",
                description="Display system notifications or alerts",
                inputSchema={
                    "type": "object",
                    "required": ["title", "message"],
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Notification title",
                        },
                        "message": {
                            "type": "string",
                            "description": "Notification message",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Duration in seconds",
                            "default": 5,
                        },
                    },
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:

        logger.info(f"CALL TOOL: {name}")
        logger.debug(f"Arguments: {arguments}")

        try:
            result = None

            # Mouse operations
            if name == "mouse_move":
                result = mouse_move(
                    arguments["x"], arguments["y"], arguments.get("duration", 0.5)
                )
            elif name == "mouse_scroll":
                result = mouse_scroll(
                    arguments["direction"],
                    arguments.get("clicks", 3),
                    arguments.get("x"),
                    arguments.get("y"),
                )
            elif name == "mouse_click":
                result = mouse_left_click(
                    arguments.get("x"),
                    arguments.get("y"),
                    arguments.get("button", "left"),
                )
            elif name == "mouse_double_click":
                result = mouse_double_click(
                    arguments.get("x"),
                    arguments.get("y"),
                    arguments.get("button", "left"),
                )
            elif name == "mouse_drag":
                result = mouse_drag(
                    arguments["start_x"],
                    arguments["start_y"],
                    arguments["end_x"],
                    arguments["end_y"],
                    arguments.get("duration", 1.0),
                    arguments.get("button", "left"),
                )

            # Keyboard operations
            elif name == "keyboard_type":
                result = keyboard_type(
                    arguments["text"], arguments.get("interval", 0.01)
                )
            elif name == "keyboard_hotkeys":
                result = keyboard_hotkeys(
                    arguments["keys"], arguments.get("interval", 0.1)
                )
            elif name == "keyboard_press":
                result = keyboard_press(
                    arguments["key"],
                    arguments.get("presses", 1),
                    arguments.get("interval", 0.1),
                )

            # Screen operations
            elif name == "take_screenshot":
                region = arguments.get("region")
                if region and len(region) == 4:
                    region = tuple(region)
                result = take_screenshot(
                    region, arguments.get("format", "PNG"), arguments.get("quality", 95)
                )
            elif name == "get_screen_size":
                result = get_screen_size()
            elif name == "get_pixel_color":
                result = get_pixel_color(arguments["x"], arguments["y"])
            elif name == "take_screenshot_with_cursor":
                region = arguments.get("region")
                if region and len(region) == 4:
                    region = tuple(region)
                result = take_screenshot_with_cursor(
                    region, arguments.get("format", "PNG"), arguments.get("quality", 95)
                )

            # Screen recording operations
            elif name == "start_recording":
                result = start_recording(arguments["filename"])
            elif name == "end_recording":
                result = end_recording(arguments["filename"])
            elif name == "get_recording":
                result = get_recording(arguments["filename"])

            # Window operations
            elif name == "launch_application":
                result = launch_application(
                    arguments["command"], arguments.get("shell", False)
                )
            elif name == "maximize_window":
                result = maximize_window(arguments["title_contains"])

            # File operations
            elif name == "download_file":
                result = download_file(
                    arguments["url"],
                    arguments["local_path"],
                    arguments.get("timeout", 30),
                )
            elif name == "list_files":
                result = list_files(
                    arguments["directory_path"],
                    arguments.get("pattern", "*"),
                    arguments.get("include_hidden", False),
                )
            elif name == "search_files":
                result = search_files(
                    arguments["directory_path"],
                    arguments["filename_pattern"],
                    arguments.get("recursive", True),
                    arguments.get("max_results", 100),
                )

            # System operations
            elif name == "get_system_info":
                result = get_system_info()
            elif name == "get_active_window":
                result = get_active_window()
            elif name == "run_python_code":
                result = run_python_code(
                    arguments["code"], arguments.get("timeout", 30)
                )
            elif name == "show_notification":
                result = show_notification(
                    arguments["title"],
                    arguments["message"],
                    arguments.get("duration", 5),
                )

            else:
                result = {"success": False, "error": f"Unknown tool: {name}"}

            logger.debug(f"Result: {result}")

            # Handle image data for screenshots
            if (
                (name == "take_screenshot" or name == "take_screenshot_with_cursor")
                and result.get("success")
                and result.get("image_data")
            ):
                import base64

                image_data = result.pop("image_data")

                # Return both metadata and image
                return [
                    types.TextContent(type="text", text=json.dumps(result)),
                    types.ImageContent(
                        type="image",
                        data=image_data,
                        mimeType=f"image/{result.get('format', 'PNG').lower()}",
                    ),
                ]
            # Handle video data for recordings
            elif (
                name == "get_recording"
                and result.get("success")
                and result.get("video_data")
            ):
                # For video data, we keep it in the result as base64
                # The client can decode and save it as needed
                result_json = json.dumps(result, indent=2)
                return [types.TextContent(type="text", text=result_json)]
            else:
                result_json = json.dumps(result, indent=2)
                return [types.TextContent(type="text", text=result_json)]

        except Exception as e:
            logger.error(f"Tool execution failed for {name}: {str(e)}", exc_info=True)
            error_result = {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
            }
            return [types.TextContent(type="text", text=json.dumps(error_result))]

    # ----------------------------------
    # SSE Server Transport
    # ----------------------------------

    session_manager = StreamableHTTPSessionManager(
        app=server,
        json_response=True,
        event_store=None,
        stateless=True,
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for managing session manager lifecycle."""
        async with session_manager.run():
            logger.info("MCP Computer Control Server started!")
            logger.info(f"Available at: http://0.0.0.0:{port}/mcp")
            try:
                yield
            finally:
                logger.info("Server shutting down...")

    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    # Run the server
    try:
        uvicorn.run(
            starlette_app,
            host="0.0.0.0",
            port=port,
            log_config=None,
            access_log=False,  # Disable access logs to prevent issues
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        serve()
    except KeyboardInterrupt:
        # Note: logger may not be available here, so using print is okay
        print("KeyboardInterrupt received. Cleaning up before exit...")
    except Exception as e:
        # Try to use logger if available, otherwise print
        try:
            logging.getLogger("mcp_computer_control").error(
                f"Server failed: {str(e)}", exc_info=True
            )
        except:
            print(f"Server failed: {str(e)}")
        sys.exit(1)
