# Echo Operator

## Structure

- `models/*`: all packages related to downloading models and simple servers that provide access to local versions of a model
- `agents/*`: agents that are used in the repo
- `ui`: a Web-based UI to help facilitate the usage of these agents
- `computer`: VMs and automation server

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

# Getting Started

## Computer

To run computer that agent controls follows documentation [here](./computers/README.md).

In case you want default way (Works on Windows and Linux) run `docker-compose up` in folder `./computers/windows/docker`.

## OmniParser

### Model Download

```
$ cd models/downloader
$ uv run download.py omniparser
```

### Start the OmniParser server

```
$ cd models/server-omniparser
$ uv run server.py
```

## Adding New Packages

1. Create a new directory under `packages/`
2. Add a `pyproject.toml` file
3. Add relative path to the package in `scripts/requirements-dev.txt` so it gets placed in the editable mode during development
4. Run `uv sync` to update dependencies
5. Run `uv pip install -e packages/xyz` to start development
