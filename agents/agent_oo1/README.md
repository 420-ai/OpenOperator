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
OLLAMA_URL=http://127.0.0.1:11434
OMNIPARSER_URL=http://127.0.0.1:8000
OPENAI_API_KEY=<API_KEY>
ANTHROPIC_API_KEY=<API_KEY>
```

## Run

```bash
uv venv
source .venv/bin/activate
uv sync
cd ..
uv run -m agent_oo1.main
```
