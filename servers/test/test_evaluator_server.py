from pprint import pprint
import requests

# BASE_URL = "http://127.0.0.1:5053"
# BASE_URL = "http://win-1.4.155.164.237.nip.io/eval"
BASE_URL = "http://test-final-2.4.242.123.121.nip.io/eval"

def test_healthcheck():
    resp = requests.get(f"{BASE_URL}/healthcheck")
    print("Healthcheck:", resp.status_code, resp.json())


def test_evaluation():
    # payload = {
    #     "telemetry_file": "teams-telemetry-1.json",
    #     "markers": [
    #         {
    #             "name": "userbins",
    #             "data.Action.Gesture": "auto",
    #             "data.Action.Scenario": "C2L2ShowChannelUnifiedAppsButton",
    #             "data.Action.ScenarioType": "channelUnifiedAppsInteraction"
    #         },
    #     ]
    # }

    payload = {
        "telemetry_file": "teams-telemetry-1.log",
        "markers": [
            {
                "name": "userbins",
                "data.Action.Scenario": "channelNav",
                "data.Action.ScenarioType": "admin",
                "data.Action.SubWorkLoad": "channelListNavigation",
                "data.Action.WorkLoad": "teamChannelManagement",
            },
            {
                "name": "userbins",
                "data.Action.Scenario": "C2L2ShowChannelUnifiedAppsButton"
            },
            {
                "name": "userbins",
                "data.Action.ScenarioType": "channelUnifiedAppsInteraction"
            },
        ]
    }

    resp = requests.post(
        f"{BASE_URL}/evaluate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print("Response JSON:")
    pprint(resp.json())



if __name__ == "__main__":
    test_healthcheck()
    # test_evaluation()
