# Run

Run locally via Ollama.

1. Download [Ollama](https://ollama.com/download)
2. Run in terminal `ollama pull mistral:latest`

# Open Web UI

If you want to test the model via [UI](https://github.com/open-webui/open-webui).

Prefered way is to use it via docker

```
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```
