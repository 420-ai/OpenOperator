# Run

```bash
uv run server.py
```

# Docker

Build

```bash
docker build --no-cache --progress=plain -t lukaskellerstein/omniparser-server:0.0.1 .
```

Run

```bash
docker run --name omniparser-server -p 8000:8000 --gpus all lukaskellerstein/omniparser-server:0.0.1
```

Push

```bash
docker push lukaskellerstein/omniparser-server:0.0.1
```
