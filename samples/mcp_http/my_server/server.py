import json
import uvicorn
from pydantic import AnyUrl
import os
import contextlib
from collections.abc import AsyncIterator

# MCP
from mcp.server.lowlevel import Server
import mcp.types as types 
from mcp.server.lowlevel.helper_types import ReadResourceContents

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

# Tools, Resources
from tools.get_stock_price import get_stock_price
from tools.get_dividend_date import get_dividend_date
from resources.read_sample_file import read_sample_file

def serve():
    server = Server("mcp-finance")

    # ----------------------------------
    # ----------------------------------
    # Tools
    # ----------------------------------
    # ----------------------------------

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="get_stock_price",
                description="Get the current stock price.",
                inputSchema={
                    "type": "object",
                    "required": ["ticker"],
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "The stock ticker symbol (e.g., AAPL, GOOG)",
                        }
                    },
                },
            ),
            types.Tool(
                name="get_dividend_date",
                description="Get the next dividend date of a stock.",
                inputSchema={
                    "type": "object",
                    "required": ["ticker"],
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "The stock ticker symbol (e.g., AAPL, GOOG)",
                        }
                    },
                },
            )
        ]


    @server.call_tool()
    async def handle_call_tool(
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


    # ---------------------------------
    # ---------------------------------
    # Resources
    # ---------------------------------
    # ---------------------------------

    @server.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                uri="string:///hello",
                name="Sample Text",
                mimeType="text/plain"
            ),
            types.Resource(
                uri="string:///sample.txt",
                name="Sample Text File's content send as string",
                mimeType="text/plain"
            ),
            types.Resource(
                uri="binary:///image",
                name="Picture in binary format",
                mimeType="image/png"
            ),
        ]
    
    @server.read_resource()
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

        elif uri == "string:///sample.txt":
            text = read_sample_file()
            return [
                ReadResourceContents(
                    content=text,
                    mime_type="text/plain"
                )
            ]

        elif uri == "binary:///image":
            image_path = os.path.join(os.path.dirname(__file__), "resources", "test_image.png")
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            return [
                ReadResourceContents(
                    content=image_bytes,
                    mime_type="image/png"
                )
            ]

        raise ValueError(f"Unknown resource: {uri}")


    # ---------------------------------
    # ---------------------------------
    # Prompts
    # ---------------------------------
    # ---------------------------------

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        return [
            types.Prompt(
                name="stock-summary",
                description="Generate a brief summary of a specific stock's recent performance.",
                arguments=[
                    types.PromptArgument(name="ticker", description="Stock ticker symbol (e.g., AAPL, TSLA)", required=True),
                    types.PromptArgument(name="days", description="Number of past days to include in the summary", required=True),
                ],
            ),
            types.Prompt(
                name="investment-evaluation",
                description="Evaluate an investment opportunity based on user-provided details.",
                arguments=[
                    types.PromptArgument(name="company_name", description="Name of the company", required=True),
                    types.PromptArgument(name="sector", description="Sector the company operates in", required=True),
                    types.PromptArgument(name="risk_tolerance", description="User's risk tolerance (low, medium, high)", required=True),
                ],
            )
        ]

    @server.get_prompt()
    async def handle_get_prompt(
        name: str, arguments: dict[str, str] | None
    ) -> types.GetPromptResult:

        if name == "stock-summary":
            ticker = arguments.get("ticker", "UNKNOWN")
            days = arguments.get("days", "7")
            return types.GetPromptResult(
                description="Prompt to summarize stock performance",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Give me a summary of {ticker} stock performance over the past {days} days."
                        ),
                    )
                ],
            )

        elif name == "investment-evaluation":
            company = arguments.get("company_name", "Unnamed Company")
            sector = arguments.get("sector", "Unknown")
            risk = arguments.get("risk_tolerance", "medium")
            return types.GetPromptResult(
                description="Prompt to evaluate an investment opportunity",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=(
                                f"Evaluate the investment opportunity in {company}, operating in the {sector} sector. "
                                f"The investor has a {risk} risk tolerance."
                            )
                        ),
                    )
                ],
            )

        else:
            raise ValueError(f"Unknown prompt: {name}")


    # ---------------------------------
    # SSE Server Transport
    # ---------------------------------

    # Create the session manager with our app and event store
    session_manager = StreamableHTTPSessionManager(
        app=server,
        json_response=True,  # Use JSON responses
        event_store=None,  # No resumability
        stateless=True,
    )

    # ASGI handler for streamable HTTP connections
    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for managing session manager lifecycle."""
        async with session_manager.run():
            print("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                print("Application shutting down...")


    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    # Run the server
    uvicorn.run(starlette_app, host="0.0.0.0", port=8002)


if __name__ == "__main__":
    print("Starting server...")
    try:
        serve()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Cleaning up before exit...")