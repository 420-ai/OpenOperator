# OO Agent

Open Operator agent.

OO version of WAA agent: https://github.com/microsoft/WindowsAgentArena

| Param        | Value                                     |
| ------------ | ----------------------------------------- |
| AI Framework | No AI Agent framework.                    |
| Agent Style  | [ReAct](https://arxiv.org/abs/2210.03629) |
| RL           | No, but possible via using Gymnasium env  |

### Azure OpenAI

In the Azure needs to exist an OpenAI resource, the name of the resource is used as `<AZURE_OPENAI_NAME>`. In the resource needs to be deployment of the `gpt-4o` model. The name of the deployment will be used as `<GPT_MODEL_DEPLOYMENT>`.

## Environment

The agent needs `.env` file with data belo

```
AZURE_API_KEY=<AZURE_OPENAI_API_KEY>
AZURE_OPENAI_BASEURL=https://<AZURE_OPENAI_NAME>.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

## Run

`uv run main.py`

# Development Notes

> The section below are only notes for Author. It is not needed to follow it

## Take Screenshot

I've replaced the way `DesktopEnv` takes screenshots (`_get_screenshot`). Instead of QEMU is used the `server` on VM.

```Python
# Replace VM QEMU screenshot with the one from the server
# screenshot = self.vm_controller.take_screenshot()
screenshot = self.controller.get_screenshot()
```

The QEMU controller does not work for me, even though I exposed the port 7200 in docker-compose file, and add the ARGUMETNS envVar in dockerfile.

> We need to make QEMU controller work, but it is not critical for now.
