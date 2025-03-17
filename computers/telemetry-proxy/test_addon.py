# mitmproxy -k -s test_addon.py --mode local --view-filter="teams.events.data.microsoft.com" --showhost

from server.teams_telemetry_addon import TeamsTelemetryAddon

addons=[TeamsTelemetryAddon()]