import sys
import asyncio

# IMPORTANT: This import must be done before importing any other asyncio-related modules
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from datetime import datetime
import os
import setproctitle
import uuid
import subprocess
import psutil
import requests
from typing import Optional
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from playwright.async_api import async_playwright
import platform
import pyautogui
import logging
import traceback
from dotenv import load_dotenv
from logging_setup import configure_logging
import pygetwindow as gw
import time

load_dotenv()

try:

    # Port
    port = os.getenv("PORT", "5051")
    print("PORT", port)

    # MCP Configuration
    MCP_PORT = int(os.getenv("MCP_PORT", "8931"))
    CDP_PORT = int(os.getenv("CDP_PORT", "9222"))
    print(f"MCP_PORT: {MCP_PORT}, CDP_PORT: {CDP_PORT}")

    # Setup logging
    logs_path = os.getenv("LOG_PATH")
    print("LOG_PATH", logs_path)
    configure_logging(logs_path)
    logger = logging.getLogger("server_browser_control")
    print("Logging configured")

    # Named the process for easier identification
    setproctitle.setproctitle("server_browser_control")

    # Paths
    traces_path = os.path.join(os.path.dirname(__file__), "traces")
    os.makedirs(traces_path, exist_ok=True)

    screenshots_path = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(screenshots_path, exist_ok=True)

    app = FastAPI()

    # We'll keep our browser and page references at the module level
    # for this simple demonstration. (Not recommended for production.)
    playwright_obj = None
    browser = None
    page = None
    pages = {}
    browser_lock = (
        asyncio.Lock()
    )  # helps to ensure thread safety if multiple requests come in

    # MCP Playwright server management
    mcp_process: Optional[subprocess.Popen] = None
    mcp_lock = asyncio.Lock()

    # ---------------------------
    # Healthcheck Endpoint
    # ---------------------------
    @app.get("/healthcheck")
    def healthcheck_endpoint():
        return {"status": "Successful", "message": "Service is operational!"}

    # ---------------------------
    # Browser Lifecycle Management
    # ---------------------------
    @app.post("/browser/launch")
    async def launch_browser(headless: bool = False):
        global playwright_obj, browser, context
        try:
            async with browser_lock:
                if browser is not None:
                    # Check if browser is actually still connected
                    try:
                        # This will fail if browser was closed manually
                        _ = browser.contexts
                        logger.info(
                            "Browser launch requested but browser is already running"
                        )
                        return {"message": "Browser is already launched"}
                    except:
                        # Browser was closed manually, clean up state
                        logger.info("Browser was closed manually, cleaning up state")
                        browser = None
                        context = None
                        pages.clear()
                        if playwright_obj:
                            await playwright_obj.stop()
                            playwright_obj = None

                # Get screen resolution
                screen_width, screen_height = pyautogui.size()
                logger.info(
                    f"Launching browser with headless={headless}, CDP port={CDP_PORT}, viewport={screen_width}x{screen_height}"
                )

                playwright_obj = await async_playwright().start()

                # Use launch_persistent_context to open a maximized browser
                user_data_dir = os.path.join(os.path.dirname(__file__), "user_data")
                os.makedirs(user_data_dir, exist_ok=True)

                context = await playwright_obj.chromium.launch_persistent_context(
                    user_data_dir,  # Required for persistent context
                    headless=headless,
                    args=[
                        f"--remote-debugging-port={CDP_PORT}",  # Enable CDP for MCP connection
                        "--no-first-run",
                        "--no-default-browser-check",
                    ],
                )

                # ----------------------------------------
                # Maximize the browser window
                # Wait a bit for the window to appear
                time.sleep(2)
                windows = gw.getWindowsWithTitle("Chromium")  # Or "Google Chrome" etc.

                if windows:
                    window = windows[0]
                    window.maximize()  # Moves to top-left and resizes to fit screen
                # ----------------------------------------

                browser = context

                # Verify CDP endpoint is accessible
                await asyncio.sleep(2)  # Give browser time to start
                try:
                    response = requests.get(
                        f"http://localhost:{CDP_PORT}/json/version", timeout=5
                    )
                    if response.status_code == 200:
                        logger.info(
                            f"CDP endpoint verified at http://localhost:{CDP_PORT}"
                        )
                    else:
                        logger.warning(
                            f"CDP endpoint returned status {response.status_code}"
                        )
                except Exception as e:
                    logger.warning(f"Could not verify CDP endpoint: {e}")

                logger.info("Browser launched successfully")
                return {
                    "message": "Browser launched successfully",
                    "cdp_port": CDP_PORT,
                }

        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Failed to launch browser: {str(e)}"
            )

    @app.post("/browser/close")
    async def close_browser():
        global playwright_obj, browser, context, pages
        try:
            async with browser_lock:
                if browser is None:
                    logger.info("Browser close requested but browser is not running")
                    return {"message": "Browser is already closed or not launched yet"}

                logger.info("Closing browser")
                await browser.close()
                await playwright_obj.stop()
                browser, playwright_obj, context, pages = None, None, None, {}
                logger.info("Browser closed successfully")

                # Also stop MCP if running
                if mcp_process and mcp_process.poll() is None:
                    logger.info("Stopping MCP server as browser is closing")
                    await stop_mcp_server()

                return {"message": "Browser closed successfully"}

        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Failed to close browser: {str(e)}"
            )

    @app.post("/browser/open")
    async def open_page(url: str = Body(..., embed=True)):
        global context, pages
        try:
            async with browser_lock:
                if context is None:
                    logger.error("Page open requested but browser is not launched")
                    raise HTTPException(
                        status_code=400, detail="Browser is not launched"
                    )

                logger.info(f"Opening new page with URL: {url}")
                page = await context.new_page()
                await page.goto(url)
                page_id = str(uuid.uuid4())
                pages[page_id] = page
                logger.info(f"Page opened successfully with ID: {page_id}")
                return {"status": "success", "page_id": page_id, "url": url}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to open page: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Failed to open page: {str(e)}"
            )

    # ---------------------------
    # CDP (Chrome DevTools Protocol)
    # ---------------------------

    @app.post("/browser/cdp")
    async def talk_cdp(
        page_id: str = Body(...),
        command: str = Body(...),
        params: dict = Body(default={}),
    ):
        try:
            if page_id not in pages:
                logger.error(f"CDP command requested for invalid page_id: {page_id}")
                raise HTTPException(status_code=400, detail="Valid page_id required")

            logger.info(f"Executing CDP command '{command}' for page_id {page_id}")
            page = pages[page_id]
            client = await page.context.new_cdp_session(page)
            result = await client.send(command, params)
            logger.info(f"CDP command '{command}' executed successfully")
            return {"result": result}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"CDP command '{command}' failed for page_id {page_id}: {str(e)}"
            )
            logger.error(traceback.format_exc())
            return JSONResponse(status_code=500, content={"error": str(e)})

    # ---------------------------
    # Browser convenience endpoints (CDP does these, but kept for convenience)
    # ---------------------------

    @app.post("/browser/screenshot")
    async def screenshot(page_id: str = Body(...)):
        if page_id not in pages:
            raise HTTPException(status_code=400, detail="Valid page_id required")

        screenshot_file_path = os.path.join(screenshots_path, f"{page_id}.png")
        await pages[page_id].screenshot(path=screenshot_file_path)
        return FileResponse(screenshot_file_path, media_type="image/png")

    @app.post("/browser/get_cookies")
    async def get_cookies(page_id: str = Body(...)):
        if page_id not in pages:
            raise HTTPException(status_code=400, detail="Valid page_id required")

        cookies = await pages[page_id].context.cookies()
        return {"cookies": cookies}

    @app.post("/browser/get_local_storage")
    async def get_local_storage(page_id: str = Body(...)):
        if page_id not in pages:
            raise HTTPException(status_code=400, detail="Valid page_id required")

        storage = await pages[page_id].evaluate("() => JSON.stringify(localStorage)")
        return {"local_storage": storage}

    @app.post("/browser/execute_js")
    async def execute_js(page_id: str = Body(...), js: str = Body(...)):
        if page_id not in pages:
            raise HTTPException(status_code=400, detail="Valid page_id required")

        result = await pages[page_id].evaluate(js)
        return {"result": result}

    # ---------------------------
    # Tracing (CDP does these, but kept for convenience)
    # ---------------------------

    @app.post("/browser/start_tracing")
    async def start_tracing():
        if context is None:
            raise HTTPException(status_code=400, detail="Browser not launched")

        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
        return {"status": "Tracing started"}

    @app.post("/browser/stop_tracing")
    async def stop_tracing():
        trace_file = os.path.join(traces_path, f"trace-{uuid.uuid4()}.zip")
        await context.tracing.stop(path=trace_file)
        return {"status": "Tracing stopped", "trace_file": trace_file}

    @app.get("/browser/download_trace")
    async def download_trace(trace_file: str):
        if not os.path.exists(trace_file):
            raise HTTPException(status_code=400, detail="Valid trace_file required")
        return FileResponse(trace_file, media_type="application/zip")

    # ---------------------------
    # System Info & Cursor Position
    # ---------------------------

    @app.get("/platform")
    async def get_platform():
        return {"platform": platform.system()}

    @app.get("/cursor_position")
    async def cursor_position():
        pos = pyautogui.position()
        return {"x": pos.x, "y": pos.y}

    # ---------------------------
    # MCP Playwright Server Management
    # ---------------------------

    def find_npx_path() -> str:
        """Find npx executable path"""
        paths = [
            r"C:\Program Files\nodejs\npx.cmd",
            r"C:\Program Files (x86)\nodejs\npx.cmd",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\npx.cmd"),
        ]

        for path in paths:
            if os.path.exists(path):
                logger.info(f"Found npx at: {path}")
                return path

        logger.warning("npx not found in common locations, using PATH")
        return "npx"

    def kill_process_tree(pid: int):
        """Kill a process and all its children"""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

            logger.info(
                f"Killing process tree for PID {pid} with {len(children)} children"
            )

            # Kill children first
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass

            # Kill parent
            try:
                parent.terminate()
            except psutil.NoSuchProcess:
                pass

            # Wait for termination
            gone, alive = psutil.wait_procs([parent] + children, timeout=5)

            # Force kill if still alive
            for p in alive:
                try:
                    p.kill()
                except psutil.NoSuchProcess:
                    pass

        except psutil.NoSuchProcess:
            pass

    def kill_processes_on_port(port: int):
        """Kill all processes listening on a specific port"""
        logger.info(f"Looking for processes on port {port}")
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Get network connections for this process
                connections = proc.connections()
                for conn in connections:
                    # Check if listening on our port
                    if conn.laddr and conn.laddr.port == port and conn.status == 'LISTEN':
                        logger.info(f"Found process {proc.info['name']} (PID: {proc.info['pid']}) listening on port {port}")
                        kill_process_tree(proc.info['pid'])
                        killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_count > 0:
            logger.info(f"Killed {killed_count} process(es) on port {port}")
            # Give time for port to be released
            time.sleep(2)
        else:
            logger.info(f"No processes found listening on port {port}")

    async def check_mcp_server(timeout: int = 30) -> bool:
        """Check if MCP server is accessible"""
        logger.info(f"Checking MCP server availability on port {MCP_PORT}")

        # Give MCP a moment to start up
        await asyncio.sleep(2)

        for i in range(timeout):
            try:
                # Try different endpoints that MCP might expose
                endpoints = [
                    f"http://localhost:{MCP_PORT}/mcp",
                    f"http://localhost:{MCP_PORT}/",
                    f"http://127.0.0.1:{MCP_PORT}/mcp",
                    f"http://127.0.0.1:{MCP_PORT}/",
                ]

                for endpoint in endpoints:
                    try:
                        response = requests.get(endpoint, timeout=1)
                        logger.debug(
                            f"Checking {endpoint}: status {response.status_code}"
                        )

                        # Any response means server is running
                        if response.status_code:
                            logger.info(
                                f"MCP server is accessible at {endpoint} after {i+1} seconds (status: {response.status_code})"
                            )
                            return True
                    except requests.exceptions.RequestException as e:
                        if i == 0:
                            logger.debug(
                                f"Endpoint {endpoint} not ready: {type(e).__name__}"
                            )
                        pass

                if i % 10 == 0 and i > 0:
                    logger.warning(f"Still waiting for MCP server... ({i}/{timeout}s)")

            except Exception as e:
                logger.error(f"Unexpected error checking MCP: {e}")

            await asyncio.sleep(1)

        logger.error(
            f"MCP server not accessible after {timeout} seconds on any endpoint"
        )
        return False

    async def stop_mcp_server():
        """Stop MCP server process"""
        global mcp_process
        if mcp_process and mcp_process.poll() is None:
            logger.info(f"Stopping MCP server process (PID: {mcp_process.pid})")
            kill_process_tree(mcp_process.pid)
            mcp_process = None
            logger.info("MCP server stopped")

    @app.post("/mcp/start")
    async def start_mcp_server():
        """Start MCP Playwright server connected to the browser via CDP"""
        global mcp_process

        try:
            async with mcp_lock:
                # Kill any existing processes on the MCP port first
                kill_processes_on_port(MCP_PORT)
                
                # If we have a reference to an existing MCP process, clean it up
                if mcp_process:
                    if mcp_process.poll() is None:
                        logger.info("Cleaning up existing MCP process reference")
                        await stop_mcp_server()
                    mcp_process = None

                # Check if browser is running
                if browser is None:
                    logger.error("MCP start requested but browser is not running")
                    raise HTTPException(
                        status_code=400, detail="Browser must be launched first"
                    )

                # Find npx
                npx_path = find_npx_path()

                # Build MCP command
                mcp_args = [
                    npx_path,
                    "@playwright/mcp@latest",
                    "--port",
                    str(MCP_PORT),
                    "--host",
                    "0.0.0.0",
                    "--output-dir",
                    "./output",
                    "--cdp-endpoint",
                    f"http://localhost:{CDP_PORT}",
                ]

                logger.info(f"Starting MCP server with command: {' '.join(mcp_args)}")

                # Change to C:\Data directory
                os.makedirs(r"C:\Data", exist_ok=True)

                # Start MCP process
                mcp_process = subprocess.Popen(
                    mcp_args,
                    cwd=r"C:\Data",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=(
                        subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                    ),
                )

                logger.info(f"MCP server process started with PID: {mcp_process.pid}")

                # Give process a moment to fail immediately if there's an error
                await asyncio.sleep(2)

                # Check if process died immediately
                if mcp_process.poll() is not None:
                    stdout, stderr = mcp_process.communicate()
                    logger.error(
                        f"MCP process died immediately with return code: {mcp_process.returncode}"
                    )
                    logger.error(f"MCP stdout: {stdout}")
                    logger.error(f"MCP stderr: {stderr}")
                    mcp_process = None
                    raise HTTPException(
                        status_code=500,
                        detail=f"MCP server failed to start: {stderr or stdout or 'Unknown error'}",
                    )

                # Wait for MCP to be ready
                if not await check_mcp_server(30):
                    logger.error("MCP server failed to start within timeout")

                    # Capture output for debugging
                    if mcp_process:
                        try:
                            stdout, stderr = mcp_process.communicate(timeout=2)
                            logger.error(f"MCP stdout: {stdout}")
                            logger.error(f"MCP stderr: {stderr}")
                        except subprocess.TimeoutExpired:
                            logger.error(
                                "Could not get MCP output - process still running"
                            )

                        mcp_process.terminate()
                        mcp_process = None

                    raise HTTPException(
                        status_code=500, detail="MCP server failed to start"
                    )

                logger.info("MCP server started successfully")
                return {
                    "message": "MCP server started successfully",
                    "pid": mcp_process.pid,
                    "mcp_port": MCP_PORT,
                    "cdp_endpoint": f"http://localhost:{CDP_PORT}",
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to start MCP server: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Failed to start MCP server: {str(e)}"
            )

    @app.post("/mcp/stop")
    async def stop_mcp_endpoint():
        """Stop MCP Playwright server"""
        try:
            async with mcp_lock:
                if mcp_process is None or mcp_process.poll() is not None:
                    logger.info("MCP stop requested but server is not running")
                    return {"message": "MCP server is not running"}

                await stop_mcp_server()
                return {"message": "MCP server stopped successfully"}

        except Exception as e:
            logger.error(f"Failed to stop MCP server: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Failed to stop MCP server: {str(e)}"
            )

    @app.get("/mcp/status")
    async def get_mcp_status():
        """Get MCP server status"""
        try:
            is_running = mcp_process is not None and mcp_process.poll() is None

            # Check if MCP endpoint is accessible
            mcp_accessible = False
            if is_running:
                try:
                    response = requests.get(
                        f"http://localhost:{MCP_PORT}/mcp", timeout=2
                    )
                    mcp_accessible = response.status_code in [200, 404]
                except:
                    pass

            return {
                "running": is_running,
                "pid": mcp_process.pid if is_running else None,
                "mcp_port": MCP_PORT,
                "mcp_accessible": mcp_accessible,
                "cdp_endpoint": f"http://localhost:{CDP_PORT}" if browser else None,
            }

        except Exception as e:
            logger.error(f"Failed to get MCP status: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Failed to get MCP status: {str(e)}"
            )

    @app.post("/mcp/restart")
    async def restart_mcp_server():
        """Restart MCP server"""
        try:
            logger.info("Restarting MCP server")
            await stop_mcp_endpoint()
            await asyncio.sleep(2)  # Give process time to fully terminate
            return await start_mcp_server()

        except Exception as e:
            logger.error(f"Failed to restart MCP server: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Failed to restart MCP server: {str(e)}"
            )

    @app.get("/mcp/logs")
    async def get_mcp_logs(lines: int = 100):
        """Get MCP server logs (if available)"""
        try:
            if mcp_process is None:
                raise HTTPException(status_code=404, detail="MCP server is not running")

            # This is a simplified version - in production you'd want proper log streaming
            return {
                "message": "Log streaming not implemented yet",
                "pid": mcp_process.pid,
                "hint": "Check C:\\Data\\output for MCP output files",
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get MCP logs: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Failed to get MCP logs: {str(e)}"
            )

    @app.post("/launch-all")
    async def launch_browser_and_mcp(headless: bool = False):
        """Convenience endpoint to launch both browser and MCP server"""
        try:
            logger.info("Launching browser and MCP server")

            # Launch browser
            browser_result = await launch_browser(headless=headless)

            # Wait a bit for browser to fully initialize
            await asyncio.sleep(3)

            # Start MCP server
            mcp_result = await start_mcp_server()

            return {
                "browser": browser_result,
                "mcp": mcp_result,
                "message": "Browser and MCP server launched successfully",
            }

        except Exception as e:
            logger.error(f"Failed to launch browser and MCP: {str(e)}")
            logger.error(traceback.format_exc())
            # Try to clean up
            try:
                await close_browser()
            except:
                pass
            raise HTTPException(
                status_code=500, detail=f"Failed to launch services: {str(e)}"
            )

    @app.post("/stop-all")
    async def stop_all_services():
        """Convenience endpoint to stop both browser and MCP server"""
        try:
            logger.info("Stopping all services")

            results = {}

            # Stop MCP first
            if mcp_process and mcp_process.poll() is None:
                results["mcp"] = await stop_mcp_endpoint()
            else:
                results["mcp"] = {"message": "MCP server was not running"}

            # Then close browser
            if browser is not None:
                results["browser"] = await close_browser()
            else:
                results["browser"] = {"message": "Browser was not running"}

            return {"results": results, "message": "All services stopped"}

        except Exception as e:
            logger.error(f"Failed to stop all services: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Failed to stop services: {str(e)}"
            )

    # ---------------------------
    # Run Server
    # ---------------------------
    print("Starting server...")
    if __name__ == "__main__":
        logger.info(
            f"Server started on port {port} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        try:
            uvicorn.run(
                "server:app",
                host="0.0.0.0",
                port=port,
                reload=False,
                log_config=None,  # Disable Uvicorn's default logging setup
            )
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            error_traceback = traceback.format_exc()
            logger.error(error_traceback)

except Exception as ee:
    logger.error("An unexpected error occurred:", ee)
    error_traceback = traceback.format_exc()
    logger.error(error_traceback)
