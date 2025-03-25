# Echo Operator

## Structure

- `agents/*`: agents that are used in the repo
- `computers/*`: computers that are controlled by agents
- `models/*`: models used by agents
- `servers/*`: servers deployed locally or in the computers
- `ui`: a Web-based UI to help facilitate the usage of these agents

---

## Getting Started

### Computer

To run computer that agent controls follows documentation [here](./computers/README.md).

In case you want default way (Works on Windows and Linux):

```
$ cd computers/windows/docker
$ docker compose up
```

### OmniParser server

Start the OmniParser server.

```
$ cd servers/server_omniparser
$ uv run server.py
```

### Agent

Start the agent.

```bash
$ cd ./agents/agent_oo4
$ uv venv
$ source .venv/bin/activate
$ uv sync
$ cd ..
$ uv run -m agent_oo4.main
```

# Docker

```bash
docker compose build --no-cache --progress=plain
```
