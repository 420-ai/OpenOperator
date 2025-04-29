import json
from pathlib import Path
from typing import List, Dict, Any


def deep_get(dictionary: Dict[str, Any], keys: str):
    """Retrieve nested value using dot notation (e.g., data.Action.Gesture)"""
    for key in keys.split('.'):
        if not isinstance(dictionary, dict):
            return None
        dictionary = dictionary.get(key)
    return dictionary


def match_marker(obj: dict, marker: dict) -> bool:
    """Check if a log object matches the given marker."""
    if obj.get("name") != marker.get("name"):
        return False

    for key, value in marker.items():
        if key == "name":
            continue
        if deep_get(obj, key) != value:
            return False
    return True


def check_teams_telemetry(filename: str, markers: List[Dict[str, str]]) -> Dict[str, Any]:
    log_path = Path(filename)
    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {filename}")

    found = []
    not_found = markers.copy()
    match_indices = []

    marker_index = 0

    with open(log_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            if marker_index >= len(markers):
                break

            marker = markers[marker_index]
            if match_marker(record, marker):
                found.append(marker)
                match_indices.append(line_num)
                marker_index += 1

    # Prepare result
    not_found = markers[len(found):]
    matched_in_order = len(found) == len(markers)

    return {
        "found": found,
        "not_found": not_found,
        "matched_in_order": matched_in_order,
        "success": matched_in_order,
    }
