import os
import sys
import asyncio
from threading import Thread, Event
import signal
import platform
import uvicorn
import logging
import traceback
import setproctitle
from datetime import datetime
from fastapi import Request

from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from fastapi import FastAPI

from addons.teams_telemetry import TeamsTelemetryAddon
from logging_setup import configure_logging

from dotenv import load_dotenv
load_dotenv()

try:

    # Port
    port = os.getenv("PORT")
    print("PORT", port)
    port = int(port)  # Convert to integer

    # Setup logging
    logs_path = os.getenv("LOG_PATH")
    print("LOG_PATH", logs_path)
    configure_logging(logs_path)
    logger = logging.getLogger("server_network_proxy")
    print("Logging configured")

    
    # Named the process for easier identification
    setproctitle.setproctitle("network_proxy_server")


    app = FastAPI(title="Mitmproxy Controller")

    # Global variables to track proxy state
    proxy_thread = None
    proxy_master = None
    stop_event = Event()
    running = False
    loop = None


    def install_mitmproxy_cert_if_needed():
        import subprocess
        import time

        cert_path = os.path.expanduser("~/.mitmproxy/mitmproxy-ca-cert.cer")
        if not os.path.exists(cert_path):
            logger.info("Waiting for mitmproxy cert to be generated...")
            for _ in range(10):  # Retry for a few seconds
                time.sleep(1)
                if os.path.exists(cert_path):
                    break
            else:
                logger.error("Certificate not found after waiting — skipping install.")
                return

        try:
            logger.debug("Checking if mitmproxy cert is already installed...")
            result = subprocess.run(
                ["certutil", "-verifystore", "Root"],
                capture_output=True, text=True, check=True
            )
            if "mitmproxy" in result.stdout.lower():
                logger.info("mitmproxy cert is already trusted.")
                return
        except subprocess.CalledProcessError as e:
            logger.warning(f"certutil check failed: {e}")

        logger.info("Installing mitmproxy certificate into Root store...")
        try:
            subprocess.run(
                ["certutil", "-addstore", "Root", cert_path],
                check=True
            )
            logger.info("mitmproxy cert installed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install mitmproxy cert: {e}")


    def run_proxy(filename: str, storeurl: str):
        global running, proxy_master, loop

        logger.info("run_proxy() started")

        if loop is None:
            loop = asyncio.new_event_loop()
            logger.debug("New asyncio event loop created")

        asyncio.set_event_loop(loop)

        opts = options.Options(
            listen_host="0.0.0.0",
            listen_port=port,
            mode=["local:msedgewebview2"],
            ssl_insecure=True,
            showhost=True,
        )
        logger.debug(f"Proxy options configured: {opts.__dict__}")

        if proxy_master is None:
            proxy_master = DumpMaster(
                opts, loop=loop, with_termlog=False, with_dumper=False
            )
            proxy_master.addons.add(TeamsTelemetryAddon(filename=filename, storeurl=storeurl))
            logger.info("DumpMaster and TeamsTelemetryAddon initialized")

        running = True

        try:
            logger.info("Starting proxy loop")
            proxy_task = loop.create_task(proxy_master.run())

            # After mitmproxy starts, install cert if needed
            install_mitmproxy_cert_if_needed()


            while not stop_event.is_set() and not proxy_task.done():
                logger.debug("Proxy running... awaiting stop_event or completion")
                loop.run_until_complete(asyncio.sleep(5))

            # If stop was requested and task is still running
            if stop_event.is_set() and not proxy_task.done():
                logger.info("Stop event set — shutting down proxy")
                proxy_master.shutdown()
                proxy_task.cancel()
                try:
                    loop.run_until_complete(proxy_task)
                except asyncio.CancelledError:
                    logger.warning("Proxy task cancelled during shutdown")
                    pass

        except Exception as e:
            logger.error(f"Proxy encountered an exception: {e}")
            logger.error(traceback.format_exc())
        finally:
            logger.info("Exiting proxy run loop")
            running = False
            stop_event.clear()


    @app.post("/start")
    async def start_proxy(request: Request):
        logger.info("Received request to start proxy")

        global proxy_thread, running

        if proxy_thread and proxy_thread.is_alive():
            logger.warning("Proxy start requested but already running")
            return {"status": "already_running", "port": port}
        
        params = await request.json()
        filename = params.get("filename", "telemetry")
        storeurl = params.get("storeurl", "http://localhost:9200")
        logger.info(f"Starting proxy with logging into filename={filename} and storeurl={storeurl}")

        stop_event.clear()
        proxy_thread = Thread(target=run_proxy, args=(filename,storeurl,))
        proxy_thread.daemon = True
        proxy_thread.start()
        logger.info("Proxy thread started")

        # Give the proxy a moment to start
        await asyncio.sleep(0.5)

        return {"status": "started", "port": port}


    @app.post("/stop")
    async def stop_proxy():
        logger.info("Received request to stop proxy")

        global proxy_thread, running

        if not proxy_thread or not proxy_thread.is_alive():
            logger.warning("Stop requested but proxy is not running")
            return {"status": "not_running"}

        # Signal the proxy thread to stop
        stop_event.set()
        logger.info("Stop event set, waiting for proxy thread to terminate")

        # Wait for the thread to finish (with timeout)
        proxy_thread.join(timeout=3.0)

        if proxy_thread.is_alive():
            logger.error("Proxy thread did not stop in time")
            return {"status": "stopping_failed"}

        logger.info("Proxy stopped successfully")
        return {"status": "stopped"}


    @app.get("/status")
    async def status():
        logger.debug("Status requested")
        return {"status": "running" if running else "stopped", "port": port}



    # ---------------------------
    # Run Server
    # ---------------------------
    if __name__ == "__main__":
        logger.info(f"Server starting on port {port} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


        def signal_handler(sig, frame):
            logger.warning(f"Signal {sig} received — shutting down")

            # Stop the proxy via the stop event
            global proxy_thread, running

            if not proxy_thread or not proxy_thread.is_alive():
                logger.debug("No proxy thread running, exiting")
                return

            # Signal the proxy thread to stop
            stop_event.set()
            logger.info("Stop event set from signal handler")

            # Wait for the thread to finish (with timeout)
            proxy_thread.join(timeout=3.0)
            logger.info("Proxy thread joined")

            sys.exit(0)

        # Register signal handlers based on platform
        signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C works on all platforms
        logger.debug("SIGINT signal handler registered")

        if platform.system() != "Windows":
            # SIGTERM is not supported on Windows
            signal.signal(signal.SIGTERM, signal_handler)
            logger.debug("SIGTERM signal handler registered")
        else:
            # On Windows, we can also handle Ctrl+Break
            try:
                signal.signal(signal.SIGBREAK, signal_handler)
                logger.debug("SIGBREAK signal handler registered (Windows only)")
            except AttributeError:
                logger.warning("SIGBREAK not supported on this Windows version")
                pass

        try:
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=port,
                log_config=None,
                timeout_graceful_shutdown=0,
            )

            logger.info("Uvicorn server started successfully")
        except Exception as e:
            logger.error(f"Exception while running Uvicorn: {e}")
            logger.error(traceback.format_exc())


except Exception as ee:
    logger.critical("Fatal error during startup")
    logger.critical(traceback.format_exc())