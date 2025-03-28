import os
import logging
import json
import uvicorn
import setproctitle
from pydantic import AnyUrl
from datetime import datetime
import traceback
from logging_setup import configure_logging
from dotenv import load_dotenv
load_dotenv()

# MCP
from mcp.server.lowlevel import Server
import mcp.types as types
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from mcp.server.lowlevel.helper_types import ReadResourceContents
 
# Tools
from tools.execute import execute_python_command

# Resources
from resources.get_screenshot import get_screenshot_with_cursor

try:

    # Port
    port = int(os.getenv("PORT", "5055"))
    print("PORT", port)

    # Setup logging
    logs_path = os.getenv("LOG_PATH")
    print("LOG_PATH", logs_path)
    configure_logging(logs_path)
    logger = logging.getLogger("server_computer_control_mcp")
    print("Logging configured")


    # Named the process for easier identification
    setproctitle.setproctitle("server_computer_control_MCP") 


    # ----------------------------------
    # Low-level MCP server
    # ----------------------------------
    app = Server("mcp-computer-control")

    # ----------------------------------
    # ----------------------------------
    # Tools
    # ----------------------------------
    # ----------------------------------

    @app.call_tool()
    async def fetch_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        logger.debug(f"CALL TOOL: {name}, {arguments}")

        result = None
        if name == "execute_python_command":
            result = execute_python_command(arguments["command"])

        logger.debug(f"RESULT: {result}")

        result_json = json.dumps(result)

        return [types.TextContent(type="text", text=result_json)]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="execute_python_command",
                description="Executes a Python command on the computer.",
                inputSchema={
                    "type": "object",
                    "required": ["command"],
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The Python command to execute.",
                        }
                    },
                },
            )
        ]


    # ----------------------------------
    # ----------------------------------
    # Resources
    # ----------------------------------
    # ----------------------------------


    @app.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                uri="string:///hello",
                name="Sample Text",
                mimeType="text/plain"
            ),
            types.Resource(
                uri="binary:///screenshot",
                name="Screenshot",
                mimeType="image/png"
            ),
        ]

    @app.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> list[ReadResourceContents]:
        logger.debug(f"READ RESOURCE: {uri}")

        # Need to convert to string
        uri = str(uri)

        if uri == "string:///hello":
            return [
                ReadResourceContents(
                    content="Hello",
                    mime_type="text/plain"
                )
            ]
        elif uri == "binary:///screenshot":
            image_bytes = get_screenshot_with_cursor()
            return [
                ReadResourceContents(
                    content=image_bytes,
                    mime_type="image/png"
                )
            ]

        raise ValueError(f"Unknown resource: {uri}")


    # ---------------------------------
    # SSE Server Transport
    # ---------------------------------

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    # ---------------------------
    # Run Server
    # ---------------------------
    print("Starting server...")
    if __name__ == "__main__":
        logger.info(f"Server started on port {port} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            # Run the server
            uvicorn.run(
                starlette_app, 
                host="0.0.0.0", 
                port=port,
                reload=False,
                log_config=None,  # Disable Uvicorn's default logging setup
            )
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            error_traceback = traceback.format_exc()
            logger.error(error_traceback)

except Exception as ee:
    logger.error("An unexpected error occurred:", ee)
    error_traceback = traceback.format_exc()
    logger.error(error_traceback)