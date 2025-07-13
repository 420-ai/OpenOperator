"""
Minimalistic test for MCP Playwright browser control
Tests basic functionality via MCP
"""

import asyncio
import requests
import time
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

# Configuration
BASE_URL = "http://192.168.2.114:5051"  # Browser control server
MCP_PORT = 8931


def ensure_browser_and_mcp():
    """Ensure browser is open and MCP is running"""
    print("1. Checking server status...")

    # Check server health
    try:
        resp = requests.get(f"{BASE_URL}/healthcheck")
        if resp.status_code != 200:
            print("   Server not reachable")
            return False
        health_data = resp.json()
        print("Health data:")
        print(health_data)
        print(f"   Server is operational")
        browser_status = health_data.get("status", "unknown")
        if browser_status:
            print(f"   Browser status: {browser_status}")
    except Exception as e:
        print(f"   Error checking server: {e}")
        return False

    # Launch browser if needed
    print("\n2. Ensuring browser is running...")
    resp = requests.post(f"{BASE_URL}/browser/launch", json={"headless": False})
    print(f"   Browser: {resp.json().get('message', 'launched')}")
    time.sleep(3)

    # Check MCP status first
    print("\n3. Checking MCP status...")
    resp = requests.get(f"{BASE_URL}/mcp/status")
    if resp.status_code == 200:
        status = resp.json()
        print(status)
        if status.get("running"):
            print(f"   MCP already running with PID: {status.get('pid')}")
            return True

    print("\n4. Starting MCP server...")
    resp = requests.post(f"{BASE_URL}/mcp/start")
    if resp.status_code == 200:
        print(f"   MCP started with PID: {resp.json().get('pid')}")
        print("   Waiting for MCP to be ready...")
        time.sleep(10)  # Give more time for MCP to start

        # Verify MCP is accessible
        try:
            test_resp = requests.get(
                f"http://{BASE_URL.split('//')[1].split(':')[0]}:{MCP_PORT}/", timeout=2
            )
            print(f"   MCP endpoint check: {test_resp.status_code}")
        except Exception as e:
            print(f"   Warning: MCP endpoint not directly accessible: {e}")
            # This might be OK, MCP might still work through SSE

        return True
    else:
        print(f"   Failed to start MCP: {resp.text}")
        error_detail = resp.json().get("detail", "Unknown error")
        print(f"   Error detail: {error_detail}")
        return False


async def test_mcp_basics():
    """Test basic MCP functionality"""
    print("\n3. Testing MCP functionality...\n")

    # Check MCP status first
    print("\nChecking MCP status...")
    resp = requests.get(f"{BASE_URL}/mcp/status")
    print(f"   MCP status: {resp.json()}")

    # Connect to MCP server
    mcp_url = f"http://{BASE_URL.split('//')[1].split(':')[0]}:{MCP_PORT}/mcp"

    async with streamablehttp_client(mcp_url, auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("   ✓ Connected to MCP")

            # Navigate to a page
            print("\n   - Navigating to example.com...")
            await session.call_tool("browser_navigate", {"url": "https://example.com"})
            print("   ✓ Navigation complete")

            # Take a screenshot
            print("\n   - Taking screenshot...")
            await session.call_tool(
                "browser_take_screenshot", {"filename": "screenshots/mcp_test.png"}
            )
            print("   ✓ Screenshot saved")

            # Get page snapshot
            print("\n   - Getting page content...")
            result = await session.call_tool("browser_snapshot", {})
            if result.content and hasattr(result.content[0], "text"):
                snapshot = result.content[0].text
                print(f"   ✓ Page snapshot retrieved ({len(snapshot)} chars)")
                print(f"   First line: {snapshot.split(chr(10))[0][:60]}...")


async def test_mcp_interactions():
    """Test more MCP functionality - form filling, clicking, keyboard"""
    print("\n4. Testing MCP interactions...\n")

    # Check MCP status first
    print("\nChecking MCP status...")
    resp = requests.get(f"{BASE_URL}/mcp/status")
    print(f"   MCP status: {resp.json()}")

    # Connect to MCP server
    mcp_url = f"http://{BASE_URL.split('//')[1].split(':')[0]}:{MCP_PORT}/mcp"

    async with streamablehttp_client(mcp_url, auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Navigate to a search page
            print("   - Navigating to DuckDuckGo...")
            await session.call_tool(
                "browser_navigate", {"url": "https://duckduckgo.com"}
            )
            print("   ✓ Navigation complete")

            # Wait for page to load
            print("\n   - Waiting for page to load...")
            await session.call_tool("browser_wait_for", {"time": 2})
            print("   ✓ Page loaded")

            # Type in search box
            print("\n   - Typing in search box...")
            await session.call_tool(
                "browser_type",
                {
                    "element": "search input field",
                    "ref": "input[name='q']",
                    "text": "OpenAI GPT-4",
                },
            )
            print("   ✓ Text typed")

            # Press Enter to search
            print("\n   - Pressing Enter...")
            await session.call_tool("browser_press_key", {"key": "Enter"})
            print("   ✓ Search submitted")

            # Wait for results
            await session.call_tool("browser_wait_for", {"time": 3})

            # Take screenshot of results
            print("\n   - Taking screenshot of results...")
            await session.call_tool(
                "browser_take_screenshot",
                {"filename": "screenshots/mcp_search_results.png"},
            )
            print("   ✓ Results screenshot saved")

            # Try to get console messages
            print("\n   - Checking console messages...")
            result = await session.call_tool("browser_console_messages", {})
            if result.content and hasattr(result.content[0], "text"):
                messages = result.content[0].text
                print(f"   ✓ Console messages retrieved: {len(messages)} chars")


def main():
    if not ensure_browser_and_mcp():
        print("Failed to setup browser and MCP")
        return

    # Run basic tests
    asyncio.run(test_mcp_basics())
    print("\n✓ Basic MCP test completed")

    # Run interaction tests
    asyncio.run(test_mcp_interactions())
    print("\n✓ Interaction MCP test completed")

    print("\n✅ All MCP tests completed successfully!")


if __name__ == "__main__":
    main()
