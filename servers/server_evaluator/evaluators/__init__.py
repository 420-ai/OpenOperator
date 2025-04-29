from .file_exist import check_file_exists
from .teams_telemetry import check_teams_telemetry

FUNCTIONS = {
    "teams_telemetry": check_teams_telemetry,
    "check_file_exists": check_file_exists,
}
