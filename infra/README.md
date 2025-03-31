# Infra

This folder contains IaC (Infrastructure as Code) for the Open Operator.

## Steps

1. Create a Azure storage

```bash
cd terraform/storage
terraform apply
```

2. Upload the `servers` into the Azure storage

```bash
cd storage-upload
uv run main.py
```

3. Create AKS - Kubernetes (k8s) cluster

```bash
cd terraform/k8s
terraform apply
```

4. Deploy OO into k8s

```bash
cd helm
???
```
