# OO Agent

Open Operator agent. + Human in the loop

[Autogen](https://github.com/microsoft/autogen) framework.

[ReAct](https://arxiv.org/abs/2210.03629) style agent.

### Azure OpenAI

In the Azure needs to exist an OpenAI resource, the name of the resource is used as `<AZURE_OPENAI_NAME>`. In the resource needs to be deployment of the `gpt-4o` model. The name of the deployment will be used as `<GPT_MODEL_DEPLOYMENT>`.

## Environment

The agent needs `.env` file with data belo

```
AZURE_API_KEY=<AZURE_OPENAI_API_KEY>
AZURE_OPENAI_BASEURL=https://<AZURE_OPENAI_NAME>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<GPT_MODEL_DEPLOYMENT>
AZURE_OPENAI_API_VERSION=2024-05-01-preview
```

## Run

`uv run main.py`

# Problems

ReAct pattern "remembers" all steps taken, and soon he run out of context length of LLM.
