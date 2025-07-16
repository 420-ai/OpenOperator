import asyncio
from asyncio import TimeoutError, wait_for
import json
import base64
import os
import time

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

# Update this to your server's address
# BASE_URL = "http://localhost:8003"
# BASE_URL = "http://0.0.0.0:8003"
# BASE_URL = "http://127.0.0.1:8003"
BASE_URL = "http://192.168.2.114:5040"


screenshots_dir = "screenshots"
os.makedirs(screenshots_dir, exist_ok=True)
recordings_dir = "recordings"
os.makedirs(recordings_dir, exist_ok=True)


async def test_ping_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            # Test initialization
            result = await session.initialize()
            print("Initialize result:")
            print(result)

            # Test ping
            ping_result = await session.send_ping()
            print("Ping result:")
            print(ping_result)


async def test_list_tools_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            print("Listing tools...")
            try:
                await session.initialize()
                tools_list = await wait_for(session.list_tools(), timeout=5.0)
                print(f"Found {len(tools_list.tools)} tools:")
                for tool in tools_list.tools:
                    print(f"  - {tool.name}: {tool.description}")
            except TimeoutError:
                print("❌ Timed out waiting for list_tools() response")


async def test_system_info_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n🔧 Testing system info tools...")

            # Test get_system_info
            try:
                print("\n📊 Getting system info...")
                result = await wait_for(
                    session.call_tool("get_system_info", {}), timeout=5.0
                )
                if result.content and hasattr(result.content[0], "text"):
                    info = json.loads(result.content[0].text)
                    if info.get("success"):
                        print(f"✅ OS: {info['os']['system']} {info['os']['release']}")
                        print(f"✅ Screen: {info['screen']['resolution']}")
                        print(f"✅ Python: {info['python']['version'].split()[0]}")
                    else:
                        print(f"❌ Error: {info.get('error')}")
            except TimeoutError:
                print("❌ Timed out getting system info")
            except Exception as e:
                print(f"❌ Error: {e}")

            # Test get_screen_size
            try:
                print("\n📐 Getting screen size...")
                result = await wait_for(
                    session.call_tool("get_screen_size", {}), timeout=5.0
                )
                if result.content and hasattr(result.content[0], "text"):
                    info = json.loads(result.content[0].text)
                    if info.get("success"):
                        print(f"✅ Screen size: {info['size']}")
                    else:
                        print(f"❌ Error: {info.get('error')}")
            except Exception as e:
                print(f"❌ Error: {e}")


async def test_mouse_operations_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n🖱️ Testing mouse operations...")

            test_cases = [
                {
                    "name": "mouse_move",
                    "arguments": {"x": 500, "y": 300, "duration": 0.5},
                },
                {
                    "name": "mouse_scroll",
                    "arguments": {"direction": "down", "clicks": 3},
                },
                {
                    "name": "mouse_click",
                    "arguments": {"x": 500, "y": 300, "button": "left"},
                },
                {
                    "name": "mouse_double_click",
                    "arguments": {"x": 500, "y": 300},
                },
                {
                    "name": "get_pixel_color",
                    "arguments": {"x": 500, "y": 300},
                },
            ]

            for test_case in test_cases:
                try:
                    print(f"\n🔧 Testing: {test_case['name']}")
                    result = await wait_for(
                        session.call_tool(test_case["name"], test_case["arguments"]),
                        timeout=5.0,
                    )
                    if result.content and hasattr(result.content[0], "text"):
                        data = json.loads(result.content[0].text)
                        if data.get("success"):
                            print(f"✅ Success: {test_case['name']}")
                            if test_case["name"] == "get_pixel_color" and "hex" in data:
                                print(f"   Color: {data['hex']}")
                        else:
                            print(f"❌ Failed: {data.get('error')}")
                except TimeoutError:
                    print(f"❌ Timed out: {test_case['name']}")
                except Exception as e:
                    print(f"❌ Error: {e}")


async def test_keyboard_operations_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n⌨️ Testing keyboard operations...")

            test_cases = [
                {
                    "name": "keyboard_type",
                    "arguments": {
                        "text": "Hello MCP Computer Control!",
                        "interval": 0.01,
                    },
                },
                {
                    "name": "keyboard_hotkeys",
                    "arguments": {"keys": "ctrl+a"},
                },
                {
                    "name": "keyboard_press",
                    "arguments": {"key": "delete", "presses": 1},
                },
            ]

            for test_case in test_cases:
                try:
                    print(f"\n🔧 Testing: {test_case['name']}")
                    result = await wait_for(
                        session.call_tool(test_case["name"], test_case["arguments"]),
                        timeout=5.0,
                    )
                    if result.content and hasattr(result.content[0], "text"):
                        data = json.loads(result.content[0].text)
                        if data.get("success"):
                            print(f"✅ Success: {test_case['name']}")
                        else:
                            print(f"❌ Failed: {data.get('error')}")
                except Exception as e:
                    print(f"❌ Error: {e}")


async def test_screenshot_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n📸 Testing screenshot...")

            try:
                result = await wait_for(
                    session.call_tool(
                        "take_screenshot", {"format": "PNG", "quality": 95}
                    ),
                    timeout=10.0,
                )

                # Screenshot returns two content items: metadata and image
                if result.content and len(result.content) >= 2:
                    # First is metadata
                    if hasattr(result.content[0], "text"):
                        metadata = json.loads(result.content[0].text)
                        if metadata.get("success"):
                            print(
                                f"✅ Screenshot captured: {metadata['size']['width']}x{metadata['size']['height']}"
                            )
                            print(f"   Format: {metadata['format']}")
                            print(f"   Data size: {metadata['data_size_bytes']} bytes")

                    # Second is image data
                    if hasattr(result.content[1], "data") and result.content[1].data:
                        # Decode base64 string to bytes
                        image_bytes = base64.b64decode(result.content[1].data)

                        file_path = os.path.join(
                            screenshots_dir, "test_screenshot_mcp.png"
                        )
                        with open(file_path, "wb") as f:
                            f.write(image_bytes)
                        print("✅ Screenshot saved to: test_screenshot_mcp.png")
                else:
                    print("❌ Unexpected response format")

            except TimeoutError:
                print("❌ Timed out taking screenshot")
            except Exception as e:
                print(f"❌ Error: {e}")


async def test_file_operations_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n📁 Testing file operations...")

            # Test list_files
            try:
                print("\n📋 Listing files in user directory...")
                import os

                result = await wait_for(
                    session.call_tool(
                        "list_files",
                        {
                            "directory_path": "C:\\Logs",
                            "pattern": "*.log",
                            "include_hidden": False,
                        },
                    ),
                    timeout=5.0,
                )
                if result.content and hasattr(result.content[0], "text"):
                    data = json.loads(result.content[0].text)
                    if data.get("success"):
                        print(f"✅ Found {data['total_files']} .txt files")
                        # Show first 3 files
                        for file in data["files"]:
                            print(f"   - {file['name']}")
                    else:
                        print(f"❌ Error: {data.get('error')}")
            except Exception as e:
                print(f"❌ Error listing files: {e}")


def test_ping():
    asyncio.run(test_ping_async())


def test_list_tools():
    asyncio.run(test_list_tools_async())


def test_system_info():
    asyncio.run(test_system_info_async())


def test_mouse_operations():
    asyncio.run(test_mouse_operations_async())


def test_keyboard_operations():
    asyncio.run(test_keyboard_operations_async())


def test_screenshot():
    asyncio.run(test_screenshot_async())


def test_file_operations():
    asyncio.run(test_file_operations_async())


async def test_screenshot_with_cursor_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n📸 Testing screenshot with cursor...")

            try:
                result = await wait_for(
                    session.call_tool(
                        "take_screenshot_with_cursor", {"format": "PNG", "quality": 95}
                    ),
                    timeout=10.0,
                )

                # Screenshot returns two content items: metadata and image
                if result.content and len(result.content) >= 2:
                    # First is metadata
                    if hasattr(result.content[0], "text"):
                        metadata = json.loads(result.content[0].text)
                        if metadata.get("success"):
                            print(
                                f"✅ Screenshot with cursor captured: {metadata['size']['width']}x{metadata['size']['height']}"
                            )
                            print(f"   Format: {metadata['format']}")
                            print(
                                f"   Cursor position: {metadata.get('cursor_position')}"
                            )
                            print(f"   Data size: {metadata['data_size_bytes']} bytes")

                    # Second is image data
                    if hasattr(result.content[1], "data") and result.content[1].data:
                        # Decode base64 string to bytes
                        image_bytes = base64.b64decode(result.content[1].data)

                        file_path = os.path.join(
                            screenshots_dir, "test_screenshot_with_cursor_mcp.png"
                        )
                        with open(file_path, "wb") as f:
                            f.write(image_bytes)
                        print(
                            "✅ Screenshot with cursor saved to: test_screenshot_with_cursor_mcp.png"
                        )
                else:
                    print("❌ Unexpected response format")

            except TimeoutError:
                print("❌ Timed out taking screenshot with cursor")
            except Exception as e:
                print(f"❌ Error: {e}")


async def test_recording_operations_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n🎥 Testing screen recording operations...")

            filename = "test_recording_mcp"

            # Start recording
            try:
                print("\n🔴 Starting screen recording...")
                result = await wait_for(
                    session.call_tool("start_recording", {"filename": filename}),
                    timeout=5.0,
                )
                if result.content and hasattr(result.content[0], "text"):
                    data = json.loads(result.content[0].text)
                    if data.get("success"):
                        print(f"✅ Recording started: {data.get('message')}")
                        print(f"   Output path: {data.get('output_path')}")
                    else:
                        print(f"❌ Failed to start recording: {data.get('error')}")
                        return
            except Exception as e:
                print(f"❌ Error starting recording: {e}")
                return

            # Record for 5 seconds
            print("⏳ Recording for 5 seconds...")
            time.sleep(5)

            # End recording
            try:
                print("\n⏹️ Ending screen recording...")
                result = await wait_for(
                    session.call_tool("end_recording", {"filename": filename}),
                    timeout=10.0,
                )
                if result.content and hasattr(result.content[0], "text"):
                    data = json.loads(result.content[0].text)
                    if data.get("success"):
                        print(f"✅ Recording ended: {data.get('message')}")
                        print(f"   File size: {data.get('file_size_bytes')} bytes")
                    else:
                        print(f"❌ Failed to end recording: {data.get('error')}")
            except Exception as e:
                print(f"❌ Error ending recording: {e}")

            # Get recording
            try:
                print("\n📥 Getting recording file...")
                result = await wait_for(
                    session.call_tool("get_recording", {"filename": filename}),
                    timeout=15.0,
                )
                if result.content and hasattr(result.content[0], "text"):
                    data = json.loads(result.content[0].text)
                    if data.get("success"):
                        print(f"✅ Recording retrieved: {data.get('filename')}")
                        print(f"   File size: {data.get('file_size_bytes')} bytes")

                        # Note: Video data is in data['video_data'] as base64
                        # For testing, we can save it to a file
                        if "video_data" in data:
                            print("   Video data available (base64 encoded)")
                            # Optionally save the video
                            video_bytes = base64.b64decode(data["video_data"])
                            video_path = os.path.join(recordings_dir, f"{filename}.mp4")
                            with open(video_path, "wb") as f:
                                f.write(video_bytes)
                            print(f"   Video saved to: {video_path}")
                    else:
                        print(f"❌ Failed to get recording: {data.get('error')}")
            except Exception as e:
                print(f"❌ Error getting recording: {e}")


async def test_multiple_recordings_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n🎥🎥 Testing multiple concurrent recordings...")

            filename1 = "test_recording_mcp_1"
            filename2 = "test_recording_mcp_2"

            # Start first recording
            try:
                print("\n🔴 Starting first recording...")
                result1 = await wait_for(
                    session.call_tool("start_recording", {"filename": filename1}),
                    timeout=5.0,
                )
                if result1.content and hasattr(result1.content[0], "text"):
                    data1 = json.loads(result1.content[0].text)
                    if data1.get("success"):
                        print(f"✅ Recording 1 started: {data1.get('message')}")
                    else:
                        print(f"❌ Failed to start recording 1: {data1.get('error')}")
                        return
            except Exception as e:
                print(f"❌ Error starting recording 1: {e}")
                return

            # Wait a bit before starting second recording
            time.sleep(2)

            # Start second recording
            try:
                print("\n🔴 Starting second recording...")
                result2 = await wait_for(
                    session.call_tool("start_recording", {"filename": filename2}),
                    timeout=5.0,
                )
                if result2.content and hasattr(result2.content[0], "text"):
                    data2 = json.loads(result2.content[0].text)
                    if data2.get("success"):
                        print(f"✅ Recording 2 started: {data2.get('message')}")
                    else:
                        print(f"❌ Failed to start recording 2: {data2.get('error')}")
            except Exception as e:
                print(f"❌ Error starting recording 2: {e}")

            # Record for 5 seconds total
            print("⏳ Recording both for 5 seconds...")
            time.sleep(5)

            # End second recording first
            try:
                print("\n⏹️ Ending second recording...")
                result2_end = await wait_for(
                    session.call_tool("end_recording", {"filename": filename2}),
                    timeout=10.0,
                )
                if result2_end.content and hasattr(result2_end.content[0], "text"):
                    data2_end = json.loads(result2_end.content[0].text)
                    if data2_end.get("success"):
                        print(f"✅ Recording 2 ended: {data2_end.get('message')}")
                        print(f"   File size: {data2_end.get('file_size_bytes')} bytes")
                    else:
                        print(f"❌ Failed to end recording 2: {data2_end.get('error')}")
            except Exception as e:
                print(f"❌ Error ending recording 2: {e}")

            # Allow first recording to continue for 2 more seconds
            time.sleep(2)

            # End first recording
            try:
                print("\n⏹️ Ending first recording...")
                result1_end = await wait_for(
                    session.call_tool("end_recording", {"filename": filename1}),
                    timeout=10.0,
                )
                if result1_end.content and hasattr(result1_end.content[0], "text"):
                    data1_end = json.loads(result1_end.content[0].text)
                    if data1_end.get("success"):
                        print(f"✅ Recording 1 ended: {data1_end.get('message')}")
                        print(f"   File size: {data1_end.get('file_size_bytes')} bytes")
                    else:
                        print(f"❌ Failed to end recording 1: {data1_end.get('error')}")
            except Exception as e:
                print(f"❌ Error ending recording 1: {e}")

            # Get both recordings
            for fname in [filename1, filename2]:
                try:
                    print(f"\n📥 Getting {fname}...")
                    result_get = await wait_for(
                        session.call_tool("get_recording", {"filename": fname}),
                        timeout=15.0,
                    )
                    if result_get.content and hasattr(result_get.content[0], "text"):
                        data_get = json.loads(result_get.content[0].text)
                        if data_get.get("success"):
                            print(f"✅ {fname} retrieved successfully")
                            print(
                                f"   File size: {data_get.get('file_size_bytes')} bytes"
                            )
                            # Save the video
                            if "video_data" in data_get:
                                video_bytes = base64.b64decode(data_get["video_data"])
                                video_path = os.path.join(
                                    recordings_dir, f"{fname}.mp4"
                                )
                                with open(video_path, "wb") as f:
                                    f.write(video_bytes)
                                print(f"   Video saved to: {video_path}")
                        else:
                            print(f"❌ Failed to get {fname}: {data_get.get('error')}")
                except Exception as e:
                    print(f"❌ Error getting {fname}: {e}")


async def test_window_operations_async():
    async with streamablehttp_client(f"{BASE_URL}/mcp", auth=None) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("\n🪟 Testing window operations...")

            # Test launch application
            try:
                print("\n🚀 Launching notepad...")
                result = await wait_for(
                    session.call_tool("launch_application", {"command": "notepad"}),
                    timeout=5.0,
                )
                if result.content and hasattr(result.content[0], "text"):
                    data = json.loads(result.content[0].text)
                    if data.get("success"):
                        print(f"✅ Application launched: {data.get('message')}")
                        time.sleep(2)  # Give it time to open
                    else:
                        print(f"❌ Failed to launch: {data.get('error')}")
            except Exception as e:
                print(f"❌ Error launching application: {e}")

            # Test maximize window
            try:
                print("\n📐 Maximizing notepad window...")
                result = await wait_for(
                    session.call_tool("maximize_window", {"title_contains": "Notepad"}),
                    timeout=5.0,
                )
                if result.content and hasattr(result.content[0], "text"):
                    data = json.loads(result.content[0].text)
                    if data.get("success"):
                        print(f"✅ Window maximized: {data.get('message')}")
                        print(f"   Matched title: {data.get('matched_title')}")
                    else:
                        print(f"❌ Failed to maximize: {data.get('error')}")
            except Exception as e:
                print(f"❌ Error maximizing window: {e}")


def test_screenshot_with_cursor():
    asyncio.run(test_screenshot_with_cursor_async())


def test_recording_operations():
    asyncio.run(test_recording_operations_async())


def test_multiple_recordings():
    asyncio.run(test_multiple_recordings_async())


def test_window_operations():
    asyncio.run(test_window_operations_async())


if __name__ == "__main__":
    print("=== MCP Computer Control Server Tests ===\n")

    test_ping()
    print("\n" + "=" * 50 + "\n")

    test_list_tools()
    print("\n" + "=" * 50 + "\n")

    test_system_info()
    print("\n" + "=" * 50 + "\n")

    test_mouse_operations()
    print("\n" + "=" * 50 + "\n")

    test_keyboard_operations()
    print("\n" + "=" * 50 + "\n")

    test_screenshot()
    print("\n" + "=" * 50 + "\n")

    test_screenshot_with_cursor()
    print("\n" + "=" * 50 + "\n")

    test_file_operations()
    print("\n" + "=" * 50 + "\n")

    test_recording_operations()
    print("\n" + "=" * 50 + "\n")

    test_multiple_recordings()
    print("\n" + "=" * 50 + "\n")

    test_window_operations()

    print("\n✅ All tests completed!")
