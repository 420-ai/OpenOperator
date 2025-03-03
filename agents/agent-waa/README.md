# WAA Agent

WindowsAgentArena agent. Source: https://github.com/microsoft/WindowsAgentArena

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
