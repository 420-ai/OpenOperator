# Evaluator server

```
$ uv run server.py
```

## how to use?

issue a HTTP POST request to the server at this endpoint: `http://127.0.0.1:5004/evaluate`. 

Use this as the JSON body:

```
{
	"evaluation": [
		{
			"evaluator": "teams_scenarios",
			"scenarios": [
				"simple_collab_switch"
			],
			"telemetry_file": "/data/logs/teams-telemetry/teams-telemetry-0.log"
		}
	]
}
```