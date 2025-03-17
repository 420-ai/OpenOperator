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

```
$ cd agents/agent_oogen3
$ uv run main.py
```

---

## Setup

### Prerequisites

- Python 3.12 or higher

### Installation

#### On Windows:

```
setup.bat
```

#### On macOS/Linux:

```
python setup.py
```

The setup script will:

1. Install `uv` if it's not already installed
2. Create a virtual environment
3. Use `uv sync` to install all packages dependencies

## Development

After activating the virtual environment:

- On Windows: `.venv\Scripts\activate.bat`
- On macOS/Linux: `source .venv/bin/activate`

You can update all dependencies using:
