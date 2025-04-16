# OO Agent

Open Operator agent.

| Param        | Value                                     |
| ------------ | ----------------------------------------- |
| AI Framework | No AI Agent framework.                    |
| Agent Style  | [ReAct](https://arxiv.org/abs/2210.03629) |
| RL           | No                                        |

### LLMs

This agent is using various LLM providers, so you need to provide URLs and API_KEYS for all of them. Depends on the version of the agent.

## Environment

The agent needs `.env` file with data below (the exact EnvVars depends on the version of the agent).

```
AZURE_API_KEY=<API_KEY>
AZURE_OPENAI_BASEURL=https://<AZURE_OPENAI_NAME>.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-01-01-preview
OPENAI_API_KEY=<API_KEY>
ANTHROPIC_API_KEY=<API_KEY>
OLLAMA_URL=http://127.0.0.1:11434
OMNIPARSER_URL=http://127.0.0.1:8000
COMPUTER_CONTROL_URL=http://127.0.0.1:5050
BROWSER_CONTROL_URL=http://127.0.0.1:5051
```

## Run

```bash
uv venv
source .venv/bin/activate
uv sync
cd ..
uv run -m agent_oo1.main
```

# Docker

Run docker commands from the forlder `agents`.

Build

```bash
docker build -f ./agent_oo1/Dockerfile -t agent-oo1 .
```

Build without cache

```bash
docker build --no-cache --progress=plain -f ./agent_oo1/Dockerfile -t agent-oo1 .
```

**Build for k8s** = architecture Linux-Amd64

```bash
docker buildx build --platform=linux/amd64 -f ./agent_oo1/Dockerfile -t agent-oo1:0.0.1 .
```

Run

```bash
docker run --name agent_oo1 agent-oo1:0.0.1
```

Tag

```bash
docker tag agent-oo1:0.0.1 lukaskellerstein/agent-oo1:0.0.1
```

Push

```bash
docker push lukaskellerstein/agent-oo1:0.0.1
```
