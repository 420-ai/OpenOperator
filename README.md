# Echo Operator

## Structure

- `packages/cli`: Command-line interface that uses the core library
- `packages/agent-waa`: a vision based agent that can leverage OmniParser and a set of tools to automate as an automation-client
- `packages/agent-oo`: a simplified vision based agent that can leverage OmniParser and a set of tools to automate as an automation-client
- `packages/automaton`: a server 

## Setup

### Prerequisites

- Python 3.9 or higher

### Installation

#### On Windows:
```
setup.bat
```

#### On macOS/Linux:
```
chmod +x setup.py
./setup.py
```

Or simply run:
```
python setup.py
```

The setup script will:
1. Install `uv` if it's not already installed
2. Create a virtual environment
3. Use `uv sync` to install all workspace packages
4. Run a test command to verify the installation

## Development

After activating the virtual environment:

- On Windows: `.venv\Scripts\activate.bat`
- On macOS/Linux: `source .venv/bin/activate`

You can update all dependencies using:

```
uv sync && uv pip install -r scripts/requirements-dev.txt
```

## Using the CLI

After installation and activating the environment, you can use the CLI:

```
ec hello
```

## Commands

### Model Commands

Download the models
```
ec model download
```

### OmniParser

Start the OmniParser server

```
ec omniparser start
```

## Adding New Packages

1. Create a new directory under `packages/`
2. Add a `pyproject.toml` file
3. Add relative path to the package in `scripts/requirements-dev.txt` so it gets placed in the editable mode during development
4. Run `uv sync` to update dependencies
5. Run `uv pip install -e packages/xyz` to start development
