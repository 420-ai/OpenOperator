#!/usr/bin/env python3
import os
import httpx
import asyncio

async def test_connection():
    server_url = os.getenv("MCP_SERVER_URL", "http://0.0.0.0:8001")
    print(f"Testing connection to: {server_url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(server_url)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:100]}...")
    except Exception as e:
        print(f"Connection failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())