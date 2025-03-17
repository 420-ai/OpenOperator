import asyncio
import threading
from typing import List

# Import mitmproxy components
from mitmproxy import options
from mitmproxy.tools import dump

from .logger import logger


class ProxyServer:
    """
    A wrapper class for mitmproxy that runs in its own thread.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        ssl_insecure: bool = False,
        addons: List = None,
        web_host: str = "127.0.0.1",
        web_port: int = 8081,
    ):
        """
        Initialize the proxy server with configuration

        Args:
            host: Host to bind proxy to
            port: Port to bind proxy to
            ssl_insecure: Skip SSL verification if True
            addons: List of mitmproxy addons to load
            web_host: Host for the web interface
            web_port: Port for the web interface
        """
        self.host = host
        self.port = port
        self.ssl_insecure = ssl_insecure
        self.web_host = web_host
        self.web_port = web_port

        # Initialize addon list with default core addons
        self.addons = addons if addons else []

        # Set up thread and events
        self._thread = None
        self._loop = None
        self._master = None
        self._running = False
        self._shutdown_event = threading.Event()

        # Captured URLs
        self.captured_urls = []

    def _create_options(self):
        """Create mitmproxy options object with our configuration"""
        opts = options.Options(
            listen_host=self.host,
            listen_port=self.port,
            ssl_insecure=self.ssl_insecure,
            # web_host=self.web_host,
            # web_port=self.web_port,
            showhost=True,
            mode=["local:ms-teams"],
        )
        return opts

    async def _run_proxy(self):
        """Run the proxy server in an async context"""
        opts = self._create_options()

        # Create master instance
        self._master = dump.DumpMaster(
            opts,
            with_termlog=False,
            with_dumper=False,
        )

        # Register addons
        for addon in self.addons:
            self._master.addons.add(addon)

        # Start the proxy server
        logger.info(f"Starting proxy server on {self.host}:{self.port}")
        try:
            await self._master.run()
        except Exception as e:
            logger.error(f"Error running proxy: {e}")
        finally:
            logger.info("Shutting down proxy server")
            if self._master:
                await self._master.shutdown()

    def _proxy_thread(self):
        """Thread function that runs the proxy event loop"""
        # Create new event loop for this thread
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            # Run the proxy server until shutdown is requested
            self._running = True
            self._loop.run_until_complete(self._run_proxy())
        except Exception as e:
            logger.error(f"Proxy thread error: {e}")
        finally:
            self._loop.close()
            self._running = False
            self._shutdown_event.set()

    def start(self):
        """Start the proxy server in its own thread"""
        if self._thread and self._thread.is_alive():
            logger.warning("Proxy server is already running")
            return

        # Clear captured URLs
        self.captured_urls = []

        # Reset shutdown event
        self._shutdown_event.clear()

        # Start the thread
        self._thread = threading.Thread(target=self._proxy_thread)
        self._thread.daemon = True
        self._thread.start()

        logger.info("Proxy server thread started")

    def stop(self, timeout=5):
        """
        Stop the proxy server

        Args:
            timeout: Time to wait for clean shutdown in seconds
        """
        if not self._thread or not self._thread.is_alive():
            logger.warning("Proxy server is not running")
            return

        # Signal the proxy to shut down
        if self._loop and self._master:
            asyncio.run_coroutine_threadsafe(self._master.shutdown(), self._loop)

        # Wait for shutdown to complete
        shutdown_success = self._shutdown_event.wait(timeout)
        if not shutdown_success:
            logger.warning(f"Proxy server did not shut down within {timeout} seconds")

        self._thread = None
        self._loop = None
        self._running = False

    @property
    def is_running(self):
        """Check if the proxy server is running"""
        return self._running and self._thread and self._thread.is_alive()

    @property
    def status(self):
        """Get the current status of the proxy server"""
        return {
            "running": self.is_running,
            "host": self.host,
            "port": self.port,
            "captured_urls_count": len(self.captured_urls),
        }
