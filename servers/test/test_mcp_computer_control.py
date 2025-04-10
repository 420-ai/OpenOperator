import asyncio
from asyncio import TimeoutError, wait_for

from mcp.client.sse import sse_client
from mcp import ClientSession

# BASE_URL = "http://127.0.0.1:5055"
BASE_URL = "http://test-11.4.155.164.237.nip.io/mcp-cc"


async def test_ping_async():
    async with sse_client(BASE_URL+ "/sse") as streams:
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
                await session.initialize()
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
                await session.initialize()
                resources = await wait_for(session.list_resources(), timeout=5.0)
                for resource in resources.resources:
                    print(f"Resource URI: {resource.uri}, Name: {resource.name}, MIMEType: {resource.mimeType}")
            except TimeoutError:
                print("❌ Timed out waiting for list_resources() response")

async def test_call_tools_async():
    async with sse_client(BASE_URL + "/sse") as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()

            test_cases = [
                {
                    "name": "mouse_move",
                    "arguments": {"x": 300, "y": 200},
                },
                {
                    "name": "mouse_scroll",
                    "arguments": {
                        "direction": "down",
                        "amount": 10,
                        "delay": 0.1,
                        "steps": 3
                    },
                },
                {
                    "name": "mouse_left_click",
                    "arguments": {},
                },
                {
                    "name": "mouse_double_click",
                    "arguments": {},
                },
                {
                    "name": "keyboard_type",
                    "arguments": {"text": "Hello, world!"},
                },
                {
                    "name": "keyboard_hotkeys",
                    "arguments": {"hotkeys": ["ctrl", "a"]},
                }
            ]

            for test_case in test_cases:
                try:
                    print(f"\n🔧 Calling tool: {test_case['name']}")
                    result = await wait_for(session.call_tool(test_case["name"], test_case["arguments"]), timeout=5.0)
                    for content in result.content:
                        print(f"✅ Result from {test_case['name']}: {content.text if hasattr(content, 'text') else content}")
                except TimeoutError:
                    print(f"❌ Timed out calling tool: {test_case['name']}")
                except Exception as e:
                    print(f"❌ Error calling tool {test_case['name']}: {e}")

def test_ping():
    asyncio.run(test_ping_async())

def test_list_tools():
    asyncio.run(test_list_tools_async())

def test_list_resources():
    asyncio.run(test_list_resources_async())

def test_call_tools():
    asyncio.run(test_call_tools_async())

if __name__ == "__main__":
    test_ping()
    test_list_tools()
    test_list_resources()
    test_call_tools()
