from flask import Flask, request, jsonify, send_file
import logging
import os
from datetime import datetime
import setproctitle
from playwright.sync_api import sync_playwright
import uuid
import platform
import pyautogui

# Setup logging
log_file = os.path.join("\\\\host.lan\\Data", "logs", "server_browser_control.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Named the process for easier identification
setproctitle.setproctitle("server_browser_control")  

app = Flask(__name__)

# Initialize Playwright browser instance
playwright = sync_playwright().start()
browser = None
context = None
pages = {}

# Traces
traces_path = os.path.join(os.path.dirname(__file__), "traces")
os.makedirs(traces_path, exist_ok=True)
# Screenshots
screenshots_path = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(screenshots_path, exist_ok=True)


# ---------------------------
# Healthcheck Endpoint
# ---------------------------
@app.route('/healthcheck', methods=['GET'])
def healthcheck_endpoint():
    # This endpoint simply returns a status 200 response with a custom message
    return jsonify({"status": "Successful", "message": "Service is operational!"}), 200


# ---------------------------
# Browser Lifecycle Management
# ---------------------------
@app.route('/browser/launch', methods=['POST'])
def launch_browser():
    global browser, context
    if browser:
        return jsonify({"error": "Browser already running"}), 400
    
    data = request.json
    headless = data.get('headless', False)

    try:
        browser = playwright.chromium.launch(
            headless=headless,
            args=['--remote-debugging-port=9222']
        )
        context = browser.new_context()
        return jsonify({"status": "Browser launched", "headless": headless}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/browser/open', methods=['POST'])
def open_page():
    global context
    if not browser or not context:
        return jsonify({"error": "Browser not launched"}), 400
    
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    page = context.new_page()
    page.goto(url)
    page_id = str(uuid.uuid4())
    pages[page_id] = page
    return jsonify({"status": "success", "page_id": page_id, "url": url})

@app.route('/browser/close', methods=['POST'])
def close_browser():
    global browser, context, pages
    if not browser:
        return jsonify({"error": "Browser not running"}), 400

    browser.close()
    browser = None
    context = None
    pages = {}
    return jsonify({"status": "Browser closed"}), 200

# ---------------------------
# CDP (Chrome DevTools Protocol)
# ---------------------------

@app.route('/browser/cdp', methods=['POST'])
def talk_cdp():
    command = request.json.get('command')
    params = request.json.get('params', {})
    page_id = request.json.get('page_id')

    if not command or not page_id:
        return jsonify({"error": "CDP command and page_id required"}), 400

    page = pages.get(page_id)
    if not page:
        return jsonify({"error": "Invalid page_id"}), 400

    client = context.new_cdp_session(page)
    result = client.send(command, params)

    return jsonify({"result": result})

# ---------------------------
# Browser convenience endpoints (CDP does these, but kept for convenience)
# ---------------------------
@app.route('/browser/screenshot', methods=['POST'])
def screenshot():
    page_id = request.json.get('page_id')
    if not page_id or page_id not in pages:
        return jsonify({"error": "Valid page_id required"}), 400

    screenshot_path = f"screenshots/{page_id}.png"
    pages[page_id].screenshot(path=screenshot_path)
    return send_file(screenshot_path, mimetype="image/png")

@app.route('/browser/get_cookies', methods=['POST'])
def get_cookies():
    page_id = request.json.get('page_id')
    if not page_id or page_id not in pages:
        return jsonify({"error": "Valid page_id required"}), 400
    
    cookies = context.cookies(pages[page_id].url)
    return jsonify({"cookies": cookies})

@app.route('/browser/start_tracing', methods=['POST'])
def start_tracing():
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    return jsonify({"status": "Tracing started"})

@app.route('/browser/stop_tracing', methods=['POST'])
def stop_tracing():
    trace_file = f"traces/trace-{uuid.uuid4()}.zip"
    context.tracing.stop(path=trace_file)
    return jsonify({"status": "Tracing stopped", "trace_file": trace_file})

@app.route('/browser/download_trace', methods=['GET'])
def download_trace():
    trace_file = request.args.get('trace_file')
    if not trace_file or not os.path.exists(trace_file):
        return jsonify({"error": "Valid trace_file required"}), 400
    return send_file(trace_file, mimetype='application/zip')

@app.route('/browser/get_local_storage', methods=['POST'])
def get_local_storage():
    page_id = request.json.get('page_id')
    if not page_id or page_id not in pages:
        return jsonify({"error": "Valid page_id required"}), 400
    
    storage = pages[page_id].evaluate("() => JSON.stringify(localStorage)")
    return jsonify({"local_storage": storage})

@app.route('/browser/execute_js', methods=['POST'])
def execute_js():
    data = request.json
    js = data.get('js')
    page_id = data.get('page_id')
    if not page_id or page_id not in pages:
        return jsonify({"error": "Valid page_id required"}), 400
    
    page = get_page(page_id)
    result = page.evaluate(js)
    return jsonify({"result": result})


# ---------------------------
# Platform Info and Cursor Position
# ---------------------------
@app.route('/platform', methods=['GET'])
def get_platform():
    return jsonify({"platform": platform.system()})

@app.route('/cursor_position', methods=['GET'])
def cursor_position():
    pos = pyautogui.position()
    return jsonify({"x": pos.x, "y": pos.y})

# ---------------------------
# System-level Endpoints (to keep)
# -----------------------
@app.route('/setup/create_file', methods=['POST'])
def create_file():
    data = request.json
    path = data.get('path')
    content = data.get('content', '')

    if not path:
        return jsonify({"error": "File path required"}), 400

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({"status": "success", "message": f"File {path} created."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/setup/open_file', methods=['POST'])
def open_file():
    path = request.json.get('path')
    if not path or not os.path.exists(path):
        return jsonify({"error": "Valid file path required"}), 400
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        else:
            cmd = 'open' if os.name == 'Darwin' else 'xdg-open'
            os.system(f"{cmd} \"{path}\"")
        return jsonify({"status": "success", "message": f"Opened {path}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------
# 🔻 System Shutdown (Careful!)
# ---------------------------
@app.route('/shutdown', methods=['POST'])
def shutdown():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 1")
    elif platform.system() == "Linux":
        os.system("shutdown now")
    elif platform.system() == "Darwin":
        os.system("shutdown -h now")
    return jsonify({"status": "Shutdown initiated"})


# ---------------------------
# Browser convenience endpoints (CDP does these, but kept for convenience)
# -----------------------

# Helper function to get page by ID
def get_page(page_id):
    page = pages.get(page_id)
    if not page:
        raise ValueError("Invalid page_id")
    return page

# ---------------------------
# Run Server
# -----------------------
if __name__ == '__main__':
    port = 6000
    logging.info(f"Server started on port {port} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    app.run(debug=True, host='0.0.0.0', port=port)
