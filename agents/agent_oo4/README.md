# OO Agent

Open Operator agent.

| Param        | Value                                                                            |
| ------------ | -------------------------------------------------------------------------------- |
| AI Framework | No AI Agent framework.                                                           |
| Agent Style  | Custom workflow - Inspired by [Plan and solve](https://arxiv.org/abs/2305.04091) |
| RL           | No, but possible via using Gymnasium env                                         |

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

`uv run main.py`
