import asyncio
from core.clients.mcp import McpServerClient 

async def main():
    client = McpServerClient("http://127.0.0.1:5055")

    try:
        print("🔌 Connecting to MCP server...")
        await client.connect()
        print("✅ Connected!")

        print("📡 Sending ping...")
        ping_response = await client.ping()
        assert ping_response is not None, "Ping response is None"
        print("✅ Ping OK:", ping_response)

        print("🛠 Listing tools...")
        tools = await client.list_tools()
        assert isinstance(tools, list), "Tools is not a list"
        assert len(tools) > 0, "No tools returned"
        print(f"✅ {len(tools)} tool(s) found:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        print("📦 Listing Resources...")
        resources = await client.list_resources()
        assert isinstance(resources, list), "Resources is not a list"
        assert len(resources) > 0, "No Resources returned"
        print(f"✅ {len(resources)} resources(s) found:")
        for res in resources:
            print(f"- {res.uri} ({res.mimeType})")

    except Exception as e:
        print("❌ Test failed:", str(e))

    finally:
        print("🔌 Disconnecting...")
        await client.disconnect()
        print("✅ Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
