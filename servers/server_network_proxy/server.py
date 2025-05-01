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
import threading
import subprocess

from mitmproxy import options, http
from mitmproxy.tools.dump import DumpMaster
from fastapi import FastAPI

from certs import ensure_mitmproxy_cert_installed
from logging_setup import configure_logging

from dotenv import load_dotenv
load_dotenv()

try:

    # Port
    port = os.getenv("PORT")
    print("PORT", port)
    port = int(port)  # Convert to integer

    # MITM Proxy Port
    proxy_port = os.getenv("PROXY_PORT")
    print("PROXY_PORT", proxy_port)
    proxy_port = int(proxy_port)  # Convert to integer

    # Setup logging
    logs_path = os.getenv("LOG_PATH")
    print("LOG_PATH", logs_path)
    configure_logging(logs_path)
    logger = logging.getLogger("server_network_proxy")
    print("Logging configured")


    # Load addons
    from addons.teams_telemetry import TeamsTelemetryAddon

    app = FastAPI(title="Mitmproxy Controller")


    # ---------------------------
    # Healthcheck Endpoint
    # ---------------------------
    @app.get('/healthcheck')
    def healthcheck_endpoint():
        return {
            "status": "Successful", 
            "message": "Service is operational!"
        }
    

    # ---------------------------
    # Network Proxy Endpoints
    # ---------------------------

    # Global variables to track proxy state
    proxy_master = None
    proxy_thread = None
    active_addon = None
    running = False
    loop = None

    def run_proxy():
        global running, proxy_master, loop

        logger.info("run_proxy() started")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.debug("New asyncio event loop created")

        opts = options.Options(
            listen_host="0.0.0.0",
            listen_port=proxy_port,
            mode=["local:msedgewebview2"],
            ssl_insecure=True,
            showhost=True,
        )
        logger.debug(f"Proxy options configured: {opts.__dict__}")

        proxy_master = DumpMaster(opts, loop=loop, with_termlog=False, with_dumper=False)
        logger.info("DumpMaster initialized")

        # ----------------------------
        # In case it is deployed to the AKS cluster, we got IP (ex. 20.20.20.21)
        # which is considered to be a public IP. 
        # => ERROR: 
        # 2025-05-01 00:33:05 - INFO - mitmproxy.proxy.server - log - client connect
        # 2025-05-01 00:33:05 - WARNING - root - client_connected - Client connection from 20.20.20.21 killed by block_global option.
        # 2025-05-01 00:33:05 - INFO - mitmproxy.proxy.server - log - client kill connection
        # 2025-05-01 00:33:05 - INFO - mitmproxy.proxy.server - log - client disconnect

        # For that reason we need to remove the "Block" addon from proxy.
        block_addon = proxy_master.addons.get("block")
        proxy_master.addons.remove(block_addon)
        logger.debug("List of current addons:")
        logger.debug(proxy_master.addons)

        # ----------------------------

        running = True

        try:
            logger.info("Starting proxy loop")
            loop.run_until_complete(proxy_master.run())
        except Exception as e:
            logger.error(f"Proxy encountered an exception: {e}")
            logger.error(traceback.format_exc())
        finally:
            logger.info("Exiting proxy run loop")
            running = False


    @app.post("/start")
    async def start_telemetry(request: Request):
        logger.info("Received request to start proxying telemetry")

        global active_addon

        params = await request.json()
        filename = params.get("filename", "telemetry")
        # storeurl = params.get("storeurl", "http://localhost:9200")

        logger.info(f"Adding telemetry addon: filename={filename}")
        # logger.info(f"Adding telemetry addon: storeurl={storeurl}")

        if not proxy_master:
            return {"status": "error", "message": "Proxy not running"}

        if active_addon:
            logger.info("Removing existing telemetry addon")
            proxy_master.addons.remove(active_addon)

        active_addon = TeamsTelemetryAddon(filename=filename)
        proxy_master.addons.add(active_addon)
        logger.info("New telemetry addon added")

        logger.debug("List of current addons:")
        logger.debug(proxy_master.addons)

        return {"status": "telemetry_started"}


    @app.post("/stop")
    async def stop_telemetry():
        global active_addon

        if not active_addon:
            logger.info("Telemetry was not running")
            return {"status": "already_stopped"}

        try:
            proxy_master.addons.remove(active_addon)
            logger.info("Telemetry addon removed")
            active_addon = None
        except Exception as e:
            logger.error(f"Failed to remove addon: {e}")
            return {"status": "error", "message": str(e)}

        return {"status": "telemetry_stopped"}


    @app.post("/shutdown")
    async def shutdown():
        logger.warning("Shutdown requested")

        def stop_uvicorn():
            asyncio.get_event_loop().call_later(1, lambda: sys.exit(0))

        Thread(target=stop_uvicorn).start()
        return {"status": "shutdown_initiated"}

    @app.get("/status")
    async def status():
        return {
            "proxy": "running" if running else "stopped",
            "telemetry": "active" if active_addon else "inactive",
            "port": proxy_port,
        }

    # ---------------------------
    # Run Server
    # ---------------------------
    if __name__ == "__main__":
        logger.info(f"Server starting on port {port} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Named the process for easier identification
        setproctitle.setproctitle("network_proxy_server")

        # Ensure the MITMProxy cert is installed
        ensure_mitmproxy_cert_installed()

        # Start proxy thread
        proxy_thread = Thread(target=run_proxy)
        proxy_thread.daemon = True
        proxy_thread.start()
        logger.info("Proxy thread started")

        # Handle signals
        def signal_handler(sig, frame):
            logger.warning(f"Signal {sig} received — shutting down")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        if platform.system() == "Windows":
            try:
                signal.signal(signal.SIGBREAK, signal_handler)
            except AttributeError:
                pass
        else:
            signal.signal(signal.SIGTERM, signal_handler)

        try:
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=port,
                log_config=None,
                timeout_graceful_shutdown=0,
            )

        except Exception as e:
            logger.error(f"Exception while running Uvicorn: {e}")
            logger.error(traceback.format_exc())


except Exception as ee:
    logger.critical("Fatal error during startup")
    logger.critical(traceback.format_exc())