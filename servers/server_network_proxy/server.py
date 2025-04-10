from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
import asyncio
from threading import Thread, Event
from fastapi import FastAPI
import uvicorn
import sys
import signal
import platform

from addons.teams_telemetry import TeamsTelemetryAddon
from logging_setup import configure_logging
import logging
import traceback
import os
from logging_setup import configure_logging

app = FastAPI(title="Mitmproxy Controller")

# Global variables to track proxy state
proxy_thread = None
proxy_master = None
stop_event = Event()
running = False
loop = None

port = 5052


def run_proxy():
    global running, proxy_master, loop

    if loop is None:
        loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    opts = options.Options(
        listen_host="0.0.0.0",
        listen_port=port,
        mode=["local:msedgewebview2"],
        ssl_insecure=True,
        showhost=True,
    )

    if proxy_master is None:
        proxy_master = DumpMaster(
            opts, loop=loop, with_termlog=False, with_dumper=False
        )
        proxy_master.addons.add(TeamsTelemetryAddon())

    running = True

    try:
        # Create a task for the proxy and add a check for the stop event
        logging.info("Starting proxy...")
        proxy_task = loop.create_task(proxy_master.run())
        while not stop_event.is_set() and not proxy_task.done():
            loop.run_until_complete(asyncio.sleep(0.25))

        # If stop was requested and task is still running
        if stop_event.is_set() and not proxy_task.done():
            logging.info("Stopping proxy...")
            proxy_master.shutdown()
            proxy_task.cancel()
            try:
                loop.run_until_complete(proxy_task)
            except asyncio.CancelledError:
                pass
    except Exception as e:
        logging.error(f"Proxy error: {e}")
    finally:
        running = False
        stop_event.clear()


@app.post("/start")
async def start_proxy():
    global proxy_thread, running

    if proxy_thread and proxy_thread.is_alive():
        return {"status": "already_running", "port": 8080}

    stop_event.clear()
    proxy_thread = Thread(target=run_proxy)
    proxy_thread.daemon = True
    proxy_thread.start()

    # Give the proxy a moment to start
    await asyncio.sleep(0.5)

    return {"status": "started", "port": 8080}


@app.post("/stop")
async def stop_proxy():
    global proxy_thread, running

    if not proxy_thread or not proxy_thread.is_alive():
        return {"status": "not_running"}

    # Signal the proxy thread to stop
    stop_event.set()

    # Wait for the thread to finish (with timeout)
    proxy_thread.join(timeout=3.0)

    if proxy_thread.is_alive():
        return {"status": "stopping_failed"}

    return {"status": "stopped"}


@app.get("/status")
async def status():
    if running:
        return {"status": "running", "port": 8080}
    return {"status": "stopped"}


if __name__ == "__main__":

    def signal_handler(sig, frame):
        # Stop the proxy via the stop event
        global proxy_thread, running

        if not proxy_thread or not proxy_thread.is_alive():
            return

        # Signal the proxy thread to stop
        stop_event.set()

        # Wait for the thread to finish (with timeout)
        proxy_thread.join(timeout=3.0)

        sys.exit(0)

    # Register signal handlers based on platform
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C works on all platforms

    if platform.system() != "Windows":
        # SIGTERM is not supported on Windows
        signal.signal(signal.SIGTERM, signal_handler)
    else:
        # On Windows, we can also handle Ctrl+Break
        try:
            signal.signal(signal.SIGBREAK, signal_handler)
        except AttributeError:
            pass

    LOG_PATH = os.getenv("LOG_PATH", r"C:\Logs")
    configure_logging(LOG_PATH)

    logger = logging.getLogger("server_network_proxy")
    logger.info("starting network proxy server...")

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_config=None,
            timeout_graceful_shutdown=0,
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        error_traceback = traceback.format_exc()
        print(error_traceback)
