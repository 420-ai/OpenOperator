from mm_agents.navi.agent import NaviAgent
from desktop_env.envs.desktop_env import DesktopEnv

model="gpt-4o"
som_origin="oss" # "a11y", "omni", "mixed-omni", "oss", "mixed-oss"
som_config=""
temparature=1

screen_width = 1920
screen_height = 1200

# ????
if som_config in ["a11y", "omni", "mixed-omni"]:
    som_config = None
elif som_config in ["oss", "mixed-oss"]:
    som_config = {
        "pipeline": ["webparse", "groundingdino", "ocr"],
        "groundingdino": {
            "prompts": ["icon", "image"]
        },
        "ocr": {
            "class_name": "TesseractOCR"
        },
        "webparse": {
            "cdp_url": f"http://{args.emulator_ip}:9222"
        }
    }


agent = NaviAgent(
            server="oai",
            model=model,
            som_config=som_config,
            som_origin=som_origin,
            temperature=temparature
        )

env = DesktopEnv(
        action_space=agent.action_space,
        screen_size=(screen_width, screen_height),
        headless=args.headless,
        require_a11y_tree=args.observation_type in ["a11y_tree", "screenshot_a11y_tree", "som"],
        emulator_ip=args.emulator_ip, #for OS running on docker
        a11y_backend=args.a11y_backend
    )