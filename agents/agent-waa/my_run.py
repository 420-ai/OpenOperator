from mm_agents.navi.agent import NaviAgent
from desktop_env.envs.desktop_env import DesktopEnv
import lib_run_single
import os
import json
import traceback
import logging

log_file = os.path.join("my_run.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# -------------------------------------------------------
# -------------------------------------------------------

model="gpt-4o"
som_origin="omni" # "a11y", "omni", "mixed-omni", "oss", "mixed-oss"
som_config=""
temparature=1

screen_width = 1920
screen_height = 1200
headless = False
observation_type = "screenshot_a11y_tree" # "a11y_tree", "screenshot_a11y_tree", "som"
emulator_ip = "127.0.0.1" # Port :5000 => Server2 on computer ["windows VM in docker"]
a11y_backend = "uia" # "uia" or "win32"

# ????
if som_origin in ["a11y", "omni", "mixed-omni"]:
    som_config = None
elif som_origin in ["oss", "mixed-oss"]:
    som_config = {
        "pipeline": ["webparse", "groundingdino", "ocr"],
        "groundingdino": {
            "prompts": ["icon", "image"]
        },
        "ocr": {
            "class_name": "TesseractOCR"
        },
        "webparse": {
            "cdp_url": f"http://{emulator_ip}:9222"
        }
    }

test_config_base_dir = "evaluation_examples_windows"
domain = "notepad"
example_id = "366de66e-cbae-4d72-b042-26390db2b145-WOS"

# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------

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
        headless=headless,
        require_a11y_tree=observation_type,
        emulator_ip=emulator_ip, #for OS running on docker
        a11y_backend=a11y_backend
    )

config_file = os.path.join(test_config_base_dir, f"examples/{domain}/{example_id}.json")
with open(config_file, "r", encoding="utf-8") as f:
    example = json.load(f)

instruction = example["instruction"]
max_steps = 15
scores = []
example_result_dir = os.path.join(test_config_base_dir, f"results/{domain}/{example_id}")
os.makedirs(example_result_dir, exist_ok=True)
args = None # FINISH

# Run example

try:
    lib_run_single.run_single_example(
        agent, 
        env, 
        example, 
        max_steps, 
        instruction, 
        args, 
        example_result_dir,
        scores
    )
except Exception as e:
    logging.error(f"Exception in {domain}/{example_id}: {e}")
    error_traceback = traceback.format_exc()
    logging.error(error_traceback)
else:
    logging.info(f"Finished {domain}/{example_id}")
finally:
    env.close()
