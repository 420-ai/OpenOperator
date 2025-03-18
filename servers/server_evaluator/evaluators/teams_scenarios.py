from typing import List, Unpack, Tuple
from models import TeamsScenariosArgs 
import json


class EvaluatorTeamsScenarios:
    def __init__(self):
        self.typing = TeamsScenariosArgs

    def evaluate(self, args: TeamsScenariosArgs) -> Tuple[bool, str]:
        scenarios = args.scenarios
        telemetry_file = args.telemetry_file

        stopped_scenarios = set()

        with open(telemetry_file, "r") as file:
            found = set()
            line = file.readline()
            while line:
                item = json.loads(line)

                if "data" in item and "Scenario" in item["data"]:
                    scenario = item["data"]["Scenario"]
                    if "Step" in scenario:
                        if (
                            isinstance(scenario, dict)
                            and scenario.get("Step") == "stop"
                        ):
                            stopped_scenarios.add(scenario.get("Name"))
                            
                line = file.readline()          
            
            for stopped_scenario in stopped_scenarios:
                if stopped_scenario in scenarios:
                    print("FOUND")
                    found.add(stopped_scenario)
                    scenarios.remove(stopped_scenario)

        success = len(found) > 0
        if not success:
            return (success, f"These scenarios were not found: {','.join(scenarios)}.")

        return (success, f"These scenarios were found: {','.join(found)}.")
