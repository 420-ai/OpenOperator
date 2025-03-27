import sys
import asyncio
# IMPORTANT: This import must be done before importing any other asyncio-related modules
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from datetime import datetime
import os
import setproctitle
import uuid
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
load_dotenv()

try:

    # Port
    port = os.getenv("PORT")
    print(port)

    # Setup logging
    logs_path = os.getenv("LOG_PATH")
    print(logs_path)

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
    browser_lock = asyncio.Lock()  # helps to ensure thread safety if multiple requests come in


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
    # Browser Lifecycle Management
    # ---------------------------
    @app.post("/browser/launch")
    async def launch_browser(headless: bool = False):
        global playwright_obj, browser, context
        async with browser_lock:
            if browser is not None:
                return {"message": "Browser is already launched"}

            playwright_obj = await async_playwright().start()

            # Use launch_persistent_context to open a maximized browser
            user_data_dir = os.path.join(os.path.dirname(__file__), "user_data")
            os.makedirs(user_data_dir, exist_ok=True)

            context = await playwright_obj.chromium.launch_persistent_context(
                user_data_dir,  # Required for persistent context
                headless=headless,
                args=["--start-maximized"],
                viewport=None  # Important to respect window size
            )
            browser = context

            return {"message": "Browser launched successfully"}

    @app.post("/browser/close")
    async def close_browser():
        global playwright_obj, browser, context, pages
        async with browser_lock:
            if browser is None:
                return {"message": "Browser is already closed or not launched yet"}
            
            await browser.close()
            await playwright_obj.stop()
            browser, playwright_obj, context, pages = None, None, None, {}
            return {"message": "Browser closed successfully"}

    @app.post("/browser/open")
    async def open_page(url: str = Body(..., embed=True)):
        global context, pages
        async with browser_lock:
            if context is None:
                raise HTTPException(status_code=400, detail="Browser is not launched")
            
            page = await context.new_page()
            await page.goto(url)
            page_id = str(uuid.uuid4())
            pages[page_id] = page
            return {"status": "success", "page_id": page_id, "url": url}

    # ---------------------------
    # CDP (Chrome DevTools Protocol)
    # ---------------------------

    @app.post("/browser/cdp")
    async def talk_cdp(page_id: str = Body(...), command: str = Body(...), params: dict = Body(default={})):
        if page_id not in pages:
            raise HTTPException(status_code=400, detail="Valid page_id required")
        try:
            page = pages[page_id]
            client = await page.context.new_cdp_session(page)
            result = await client.send(command, params)
            return {"result": result}
        except Exception as e:
                logging.error(f"CDP command '{command}' failed for page_id {page_id}: {str(e)}")
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
        return FileResponse(trace_file, media_type='application/zip')


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
    # Run Server
    # ---------------------------
    print("Starting server...")
    if __name__ == "__main__":
        logger.info(f"Server started on port {port} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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