#!/usr/bin/env python3

import sys
import signal
import uvicorn

import logging

from server import app, proxy_server


def main():
    """Main function to run the FastAPI server"""

    # Set up signal handling for clean shutdown
    def signal_handler(sig, frame):
        logging.info("Shutdown signal received, stopping servers...")
        if proxy_server.is_running:
            proxy_server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the FastAPI server
    logging.info("Starting telemetry proxy API...")
    uvicorn.run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
