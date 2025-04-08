# Prerequisites

1. Create an `.env` file

```
AZURE_STORAGE_CONNECTION_STRING=<CONNECTION_STRING>
```

# Upload a .iso

1. In the Azure storage (`File shares`), create a folder `my-iso` and subfolder `windows-11`.
2. Upload a .iso file for Windows 11 installation (viz [link](../../computers/windows/docker/README.md) section 1.1).

# Upload OO servers

1. Run script

```bash
uv run main_servers.py
```

# Upload a Windows related data

In order to prepare Windows OS for OO needs. We need to provide some of the initialization code.

- Init script
- install.bat
- ...etc.

1. Run script

```bash
uv run main_windows.py
```
