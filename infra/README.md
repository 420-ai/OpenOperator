# Infra

This folder contains code relevant to the IaC (Infrastructure as Code) for the Open Operator.

## Storage upload

We upload a files relevant for the Computers in k8s via script.

```bash
cd storage-upload
uv run main_servers.py
uv run main_windows.py
```
