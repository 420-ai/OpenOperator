# Echo Operator

## Structure

- `agents/*`: agents that are used in the repo
- `computers/*`: computers that are controlled by agents
- `models/*`: models used by agents
- `servers/*`: servers deployed locally or in the computers
- `ui`: a Web-based UI to help facilitate the usage of these agents

---

## Getting Started

The easiest way to run OpenOperator [OO] is via command `docker compose up` in the root of the project. If you want to run just a pieces of OO, you can either comment out parts of the compose.yml

### Computer

To run computer that agent controls follows documentation [here](./computers/README.md).

In case you want default way (Works on Windows and Linux):

```bash
cd computers/windows/docker
docker compose up
```

### OmniParser server

Start the OmniParser server.

```bash
cd servers/server_omniparser
uv run server.py
```

### Agent

Start the agent.

```bash
cd ./agents/agent_oo4
uv venv
source .venv/bin/activate
uv sync
cd ..
uv run -m agent_oo4.main
```

### Analytics

We are using Elasticsearch and Kibana to observe logs and telemetry.

Open `http://localhost:5601`

# TODO

Deploy new versions of Servers and Windows-scripts into OOStorage

Test to install new computer with new server and test it !!

Deploy ElasticSearch, Kibana and Grafana into k8s

- OOObservability => new nodepool
