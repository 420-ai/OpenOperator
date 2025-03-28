from mcp.client.sse import sse_client
from mcp import ClientSession
from contextlib import asynccontextmanager
import base64
import os

class McpServerClient:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self.session = None
        self._sse_cleanup = None
        self._session_cleanup = None

    @asynccontextmanager
    async def _start_sse(self):
        async with sse_client(f"{self.server_url}/sse") as streams:
            yield streams

    async def connect(self):
        self._sse_cleanup = self._start_sse()
        read_stream, write_stream = await self._sse_cleanup.__aenter__()

        self._session_cleanup = ClientSession(read_stream, write_stream)
        self.session = await self._session_cleanup.__aenter__()

        await self.session.initialize()

    async def disconnect(self):
        if self._session_cleanup:
            await self._session_cleanup.__aexit__(None, None, None)
            self._session_cleanup = None
            self.session = None
        if self._sse_cleanup:
            await self._sse_cleanup.__aexit__(None, None, None)
            self._sse_cleanup = None

    async def ping(self):
        if not self.session:
            raise RuntimeError("Client not connected.")
        return await self.session.send_ping()

    async def list_tools(self):
        if not self.session:
            raise RuntimeError("Client not connected.")
        response = await self.session.list_tools()
        return response.tools

    async def call_tool(self, tool_name: str, parameters: dict):
        if not self.session:
            raise RuntimeError("Client not connected.")
        response = await self.session.call_tool(tool_name, parameters)
        return response.content

    async def list_resources(self):
        if not self.session:
            raise RuntimeError("Client not connected.")
        response = await self.session.list_resources()
        return response.resources

    async def read_resource(self, resource_uri: str):
        if not self.session:
            raise RuntimeError("Client not connected.")
        return await self.session.read_resource(resource_uri)

    async def save_binary_resource(self, resource_uri: str, output_path: str):
        if not self.session:
            raise RuntimeError("Client not connected.")
        resource = await self.read_resource(resource_uri)
        base64_blob = resource.contents[0].blob
        binary_data = base64.urlsafe_b64decode(base64_blob)
        with open(output_path, "wb") as f:
            f.write(binary_data)
