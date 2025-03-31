# Deploy

From this folder run commands below.

## Prerequisites

For Traefik we need to install custom CRDs (IngressRoute) via: https://doc.traefik.io/traefik/providers/kubernetes-crd/

```
# Install Traefik Resource Definitions:
kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v3.3/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml

# Install RBAC for Traefik:
kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v3.3/docs/content/reference/dynamic-configuration/kubernetes-crd-rbac.yml
```

## Proxy

Install

```Bash
helm install proxy-release ./proxy --namespace traefik --create-namespace
```

Upgrade

```bash
helm upgrade proxy-release ./proxy --namespace traefik
```

## Dockur

Install

```Bash
helm install temp-computer-release ./temp-computer --namespace tempcomp --create-namespace
```

Upgrade

```bash
helm upgrade temp-computer-release ./temp-computer --namespace tempcomp
```

## Computers

Install

```Bash
helm install windows-computers-release ./windows-computer --namespace computers --create-namespace
```

Upgrade

```bash
helm upgrade windows-computers-release ./windows-computer --namespace computers
```

## Agents

Install

```Bash
helm install agents-release ./agents --namespace agents --create-namespace
```

Upgrade

```bash
helm upgrade agents-release ./agents --namespace agents
```
