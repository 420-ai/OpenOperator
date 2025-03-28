import asyncio
from core.clients.mcp import McpServerClient

async def main():
    client = McpServerClient("http://127.0.0.1:5055")

    try:
        print("🔌 Connecting to MCP server...")
        await client.connect()
        print("✅ Connected!")

        # ------------------------------------
        # ------------------------------------
        # Tools
        # ------------------------------------
        # ------------------------------------

        print("🛠 Listing tools...")
        tools = await client.list_tools()
        assert isinstance(tools, list), "Tools is not a list"
        assert len(tools) > 0, "No tools returned"
        tool_names = {tool.name for tool in tools}
        print(f"✅ {len(tools)} tool(s) found:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        print("🧪 Calling tools...")
        test_cases = [
            {
                "name": "mouse_move",
                "arguments": {"x": 300, "y": 300},
            },
            {
                "name": "mouse_scroll",
                "arguments": {
                    "direction": "up",
                    "amount": 5,
                    "delay": 0.1,
                    "steps": 2
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
                "arguments": {"text": "MCP test input"},
            },
            {
                "name": "keyboard_hotkeys",
                "arguments": {"hotkeys": ["ctrl", "s"]},
            }
        ]

        for case in test_cases:
            if case["name"] not in tool_names:
                print(f"⚠️ Skipping unknown tool: {case['name']}")
                continue

            try:
                print(f"\n🔧 Calling tool: {case['name']} with arguments {case['arguments']}")
                result = await client.call_tool(case["name"], case["arguments"])
                assert result is not None, f"No result from {case['name']}"
                for content in result.contents:
                    if hasattr(content, "text"):
                        print(f"✅ Output: {content.text}")
                    else:
                        print(f"ℹ️ Non-text result: {content}")
            except Exception as e:
                print(f"❌ Error calling tool {case['name']}: {e}")

        # ------------------------------------
        # ------------------------------------
        # Resources
        # ------------------------------------
        # ------------------------------------

        print("📦 Listing resources...")
        resources = await client.list_resources()
        assert isinstance(resources, list), "Resources is not a list"
        assert len(resources) > 0, "No resources returned"
        print(f"✅ {len(resources)} resource(s) found:")
        for res in resources:
            print(f"  - {res.uri} ({res.mimeType})")


    except Exception as e:
        print("❌ Test failed:", str(e))

    finally:
        print("\n🔌 Disconnecting...")
        await client.disconnect()
        print("✅ Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
