# Agents

This folder contains all packages for OO Agents.

## Structure

- `agent_*`: agents versions
- `configs/*`: global configurations for particular use case (ex. software + instruction)
- `core/*`: package shared among all agents
- `functions/*`: independent functions that are triggered by configs

## Run agent

1. Go to the agent directory (ex. `cd agent_oo1`)
2. Open virtual environment

```bash
uv venv
source .venv/bin/activate
```

3. Install dependencies

```bash
uv sync
```

4. Go one level up in folders !!!

```bash
cd ..
```

You should end up in the folder `<folder_with_the_projects>/OpenOperator/agents`

5. Run agent as a module

```bash
python -m agent_oo1.main
```

or

```bash
uv run -m agent_oo1.main
```

## pyproject.toml

You have to reference the shared `core` and `functions` packages as follows in pyproject.toml for each agent.

```
dependencies = ["core", "functions"]

[tool.uv.sources]
core = { path = "../core" }
functions = { path = "../functions" }
```

## Docker

Run commands from this folder.

Build

```bash
docker build --no-cache --progress=plain -f ./agent_oo1/Dockerfile -t agent-oo1 .
```

Run

```bash
docker run --name agent-oo1 agent-oo1:latest
```
