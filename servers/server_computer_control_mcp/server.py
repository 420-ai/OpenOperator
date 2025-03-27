print("Starting server...2")

import os
import logging
import json
import uvicorn
import setproctitle

# MCP
from mcp.server.lowlevel import Server
import mcp.types as types
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route

# Tools
from tools.get_stock_price import get_stock_price
from tools.get_dividend_date import get_dividend_date


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

    @app.call_tool()
    async def fetch_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:

        print("CALL TOOL")
        print(name)
        print(arguments)

        result = None
        if name == "get_stock_price":
            result = get_stock_price(arguments["ticker"])
        elif name == "get_dividend_date":
            result = get_dividend_date(arguments["ticker"])

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
            ),
            types.Tool(
                name="get_screenshot",
                description="Get a screenshot of the computer screen.",
                inputSchema=None
            )
        ]

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