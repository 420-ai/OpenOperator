# mitmproxy -k -s test_addon.py --mode local --view-filter="teams.events.data.microsoft.com" --showhost

from addons.teams_telemetry import TeamsTelemetryAddon

addons=[TeamsTelemetryAddon()]