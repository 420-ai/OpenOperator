# Teams Telemetry Proxy

This proxy server captures Teams telemetry from the Desktop (webview2 based) into a file in a configurable place.

## Running this module

```
$ uv run main.py
```

You will then be able to access this server on port 5000. Send a `/start` POST request to start the proxy, and a `/stop` POST request to stop

i.e. POST `http://127.0.0.1:5000/start`