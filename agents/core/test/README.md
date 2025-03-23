# Tests

This folder contains test relevant to `Core` package.

## Prerequisites

Be located in the folder `core`.

1. Open virtual environment

```bash
uv venv
source .venv/bin/activate
```

2. Install dependencies

```bash
uv sync
```

3. Go one level up in folder structure

```bash
cd ..
```

So you should be on the path `<folder_with_the_projects>/OpenOperator/agents` and you should be inside the virtual environment `.venv` (viz `source .venv/bin/activate`).

Whoallaa, now you can run the tests.

## Run

You can run any test via comman `python -m core.tests.<module>.<test>`

# LLM Clients tests

## Vendor-specific clients

These commands are testing vendor specific clients.

**OpenAI**

```bash
python -m core.test.llm_clients.test_openai_client
```

**Azure OpenAI**

```bash
python -m core.test.llm_clients.test_azure_openai_client
```

**Ollama**

```bash
python -m core.test.llm_clients.test_ollama_client
```

**Anthropic**

```bash
python -m core.test.llm_clients.test_anthropic_client
```

## Vendor-agnostic client

These commands are testing vendor **agnostic** client. This client is a wrapper around the specific clients for each vendor.

**ALL**

```bash
python -m core.test.llm_clients.test_universal_llm_client
```

# SoM tests

```bash
python -m core.test.som_clients.test_omniparser
```
