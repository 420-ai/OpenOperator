from fastapi import FastAPI

from .proxy_models import ProxyConfig, ProxyResponse
from .proxy_server import ProxyServer
from .teams_telemetry_addon import TeamsTelemetryAddon

# Create FastAPI app
app = FastAPI(
    title="Telemetry Proxy API",
    description="Control and monitor the telemetry proxy server",
)

# Create a global proxy server instance
proxy_server_instance = ProxyServer(
    host="0.0.0.0", port=8080, web_host="127.0.0.1", web_port=8081
)

proxy_server_instance.addons.append(TeamsTelemetryAddon())


# Define API endpoints
@app.get("/", response_model=ProxyResponse)
def root():
    """Get basic server information"""
    return {
        "status": "success",
        "message": "Telemetry proxy API is running",
        "data": {"proxy_status": proxy_server_instance.status},
    }


@app.post("/start", response_model=ProxyResponse)
def start_proxy(config: ProxyConfig = None):
    """Start the telemetry proxy server"""
    if proxy_server_instance.is_running:
        return {
            "status": "warning",
            "message": "Proxy server is already running",
            "data": proxy_server_instance.status,
        }

    if config:
        proxy_server_instance.host = config.host
        proxy_server_instance.port = config.port

    proxy_server_instance.start()

    return {
        "status": "success",
        "message": f"Proxy server started on {proxy_server_instance.host}:{proxy_server_instance.port}",
        "data": proxy_server_instance.status,
    }


@app.post("/stop", response_model=ProxyResponse)
def stop_proxy():
    """Stop the telemetry proxy server"""
    if not proxy_server_instance.is_running:
        return {
            "status": "warning",
            "message": "Proxy server is not running",
            "data": proxy_server_instance.status,
        }

    proxy_server_instance.stop()

    return {
        "status": "success",
        "message": "Proxy server stopped",
        "data": proxy_server_instance.status,
    }


@app.get("/status", response_model=ProxyResponse)
def get_status():
    """Get the current status of the telemetry proxy server"""
    return {
        "status": "success",
        "message": "Current proxy server status",
        "data": proxy_server_instance.status,
    }
