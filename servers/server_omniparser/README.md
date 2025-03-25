# Run

```bash
uv run server.py
```

# Docker

Build

```bash
docker build --no-cache --progress=plain -t omniparser-server .
```

Run

```bash
docker run --name omniparser-server -p 8000:8000 --gpus all omniparser-server:latest
```
