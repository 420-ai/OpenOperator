# Model princing

Config section for model pricing is for 1M Tokens in USD.

```json
"models": [
    {
    "name": "o3-mini",
    "input": 1.1,
    "output": 4.4
    },
    {
    "name": "gpt-4o",
    "input": 2.5,
    "output": 10
    },
    {
    "name": "gpt-4o-mini",
    "input": 0.15,
    "output": 0.6
    }
],
```

Name of the model aligns with the name in the Autogen object.

```python
llm_o3_mini = AzureOpenAIChatCompletionClient(
    model="o3-mini",
    azure_deployment="o3-mini-deployment",
    azure_endpoint=AZURE_OPENAI_BASEURL,
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=AZURE_API_KEY,
)
```
