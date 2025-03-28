import asyncio
import os
import base64

from mcp.client.sse import sse_client
from mcp import ClientSession

from pydantic import AnyUrl, TypeAdapter

async def start():

    server_url = "http://127.0.0.1:5055" 

    async with sse_client(server_url + "/sse") as streams:
        async with ClientSession(*streams) as session:
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

        
            # -------------
            # Resources
            # -------------

            # List resources
            resources_list_response = await session.list_resources()
            print("Available resources:")
            for resource in resources_list_response.resources:
                print(f"Resource URI: {resource.uri}, Name: {resource.name}, MIMEType: {resource.mimeType}")

           