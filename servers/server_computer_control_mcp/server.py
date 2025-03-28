import os
import logging
import json
import uvicorn
import setproctitle
from pydantic import AnyUrl

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

# Port
port = os.getenv("PORT")


# Setup logging
logs_path = os.getenv("LOG_PATH")
log_file = os.path.join(logs_path, "server_computer_control_mcp.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
     format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
)

# Named the process for easier identification
setproctitle.setproctitle("server_computer_control") 


def serve():
    print("Serve()")

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

        print("CALL TOOL")
        print(name)
        print(arguments)

        result = None
        if name == "execute_python_command":
            result = execute_python_command(arguments["command"])

        print("Result:")
        print(result)

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

    # Run the server
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    print("Starting server...2")
    try:
        serve()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Cleaning up before exit...")