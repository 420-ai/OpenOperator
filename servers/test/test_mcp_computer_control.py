import asyncio
from asyncio import TimeoutError, wait_for

from mcp.client.sse import sse_client
from mcp import ClientSession

BASE_URL = "http://127.0.0.1:5055"

async def test_ping_async():
    async with sse_client(BASE_URL + "/sse") as streams:
        async with ClientSession(*streams) as session:
            print("Initializing session...")
            init_result = await session.initialize()
            print("Init result:", init_result)

            print("Sending ping...")
            ping_result = await session.send_ping()
            print("Ping result:", ping_result)

async def test_list_tools_async():
    async with sse_client(BASE_URL + "/sse") as streams:
        async with ClientSession(*streams) as session:
            print("Listing tools...")
            try:
                tools_list = await wait_for(session.list_tools(), timeout=5.0)
                for tool in tools_list.tools:
                    print(f"Tool name: {tool.name}, Description: {tool.description}")
            except TimeoutError:
                print("❌ Timed out waiting for list_tools() response")

async def test_list_resources_async():
    async with sse_client(BASE_URL + "/sse") as streams:
        async with ClientSession(*streams) as session:
            print("Listing resources...")
            try:
                resources = await session.list_resources()
                for resource in resources.resources:
                    print(f"Resource URI: {resource.uri}, Name: {resource.name}, MIMEType: {resource.mimeType}")
            except TimeoutError:
                print("❌ Timed out waiting for list_tools() response")

def test_ping():
    asyncio.run(test_ping_async())

def test_list_tools():
    asyncio.run(test_list_tools_async())

def test_list_resources():
    asyncio.run(test_list_resources_async())

if __name__ == "__main__":
    test_ping()
    test_list_tools()
    test_list_resources()
