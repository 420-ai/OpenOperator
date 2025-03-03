# WAA Agent

WindowsAgentArena agent. Source: https://github.com/microsoft/WindowsAgentArena

### Azure OpenAI

In the Azure needs to exist an OpenAI resource, the name of the resource is used as `<AZURE_OPENAI_NAME>`. In the resource needs to be deployment of the `gpt-4o` model. The name of the deployment will be used as `<GPT_MODEL_DEPLOYMENT>`

## Environment

The agent needs `.env` file with data belo

```
AZURE_API_KEY=<API_KEY>
AZURE_ENDPOINT=https://<AZURE_OPENAI_NAME>.openai.azure.com/openai/deployments/<GPT_MODEL_DEPLOYMENT>/chat/completions?api-version=2024-08-01-preview
```

## Run

`uv run my_run.py`

# Development Notes

## Take Screenshot

I've replaced the way `DesktopEnv` takes screenshots (`_get_screenshot`). Instead of QEMU is used the `server` on VM.

```Python
# Replace VM QEMU screenshot with the one from the server
# screenshot = self.vm_controller.take_screenshot()
screenshot = self.controller.get_screenshot()
```

The QEMU controller does not work for me, even though I exposed the port 7200 in docker-compose file, and add the ARGUMETNS envVar in dockerfile.

> We need to make QEMU controller work, but it is not critical for now.
