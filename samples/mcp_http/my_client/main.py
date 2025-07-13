import asyncio
import os
import base64

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession


async def start():

    tool_name = "get_stock_price"  # Tool to call (e.g., "get_stock_price" or "get_dividend_date")
    ticker = "MSFT"  # Default stock ticker
    
    server_url = "http://localhost:8002"  # URL of the MCP server

    async with streamablehttp_client(
        f"{server_url}/mcp", auth=None
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            # Test initialization
            result = await session.initialize()
            print("Initialize result:")
            print(result)

            # Test ping
            ping_result = await session.send_ping()
            print("Ping result:")
            print(ping_result)

            # -------------
            # Tools
            # -------------

            # List tools
            tools_list_response = await session.list_tools()
            print("Available tools:")
            for tool in tools_list_response.tools:
                print(f"Tool name: {tool.name}, Description: {tool.description}")

            # Call the tool
            response = await session.call_tool(tool_name, {"ticker": ticker})
            print("Tool response:")
            print(response.content)

            # -------------
            # Resources
            # -------------

            # List resources
            resources_list_response = await session.list_resources()
            print("Available resources:")
            for resource in resources_list_response.resources:
                print(f"Resource URI: {resource.uri}, Name: {resource.name}, MIMEType: {resource.mimeType}")

            # Get a specific resource
            print("--" * 20)

            # Get a string
            resource0_file = "string:///hello"
            resource0 = await session.read_resource(resource0_file)
            print(f"Resource '{resource0_file}' content:")
            print(resource0)

            print("--" * 20)

            # Get a text file content as string
            resource01_file = "string:///sample.txt"
            resource01 = await session.read_resource(resource01_file)
            print(f"Resource {resource01_file} content:")
            print(resource01)

            print("--" * 20)

            resource2_file = "binary:///image"
            resource2 = await session.read_resource(resource2_file)
            resource2_base64 = resource2.contents[0].blob
            resource2_bytes = base64.urlsafe_b64decode(resource2_base64)
            
            # save the image to a file
            output_path = os.path.join(os.path.dirname(__file__), "saved_image.png")
            with open(output_path, "wb") as f:
                f.write(resource2_bytes)

            print("--" * 20)

            # -------------
            # Prompts
            # -------------
            
            # List prompts
            print("\n=== Available Prompts ===")
            prompts_list_response = await session.list_prompts()
            for prompt in prompts_list_response.prompts:
                print(f"- {prompt.name}: {prompt.description}")

            # Get 'stock-summary' prompt
            print("\n=== Get Prompt: stock-summary ===")
            stock_prompt = await session.get_prompt(
                "stock-summary",
                arguments={"ticker": "AAPL", "days": "5"}
            )
            for msg in stock_prompt.messages:
                print(f"{msg.role}: {msg.content.text}")

            # Get 'investment-evaluation' prompt
            print("\n=== Get Prompt: investment-evaluation ===")
            invest_prompt = await session.get_prompt(
                "investment-evaluation",
                arguments={
                    "company_name": "Tesla",
                    "sector": "Automotive",
                    "risk_tolerance": "high"
                }
            )
            for msg in invest_prompt.messages:
                print(f"{msg.role}: {msg.content.text}")    

if __name__ == "__main__":
    asyncio.run(start())