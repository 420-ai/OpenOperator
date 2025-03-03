from mm_agents.navi.agent import NaviAgent
from desktop_env.envs.desktop_env import DesktopEnv
import os
import json
import traceback
import logging
from pathlib import Path
import datetime
import json
import logging
import os
import time
import traceback
from trajectory_recorder import TrajectoryRecorder

from dotenv import load_dotenv


load_dotenv()

# print("Environment variables")
# print(os.getenv("AZURE_API_KEY"))
# print(os.getenv("AZURE_ENDPOINT"))

# Logging
os.makedirs("logs", exist_ok=True)
log_file = os.path.join("logs/main.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main-agent-oo")

# -------------------------------------------------------
# -------------------------------------------------------

server="azure" # "oai", "azure"
model="gpt-4o"
som_origin="omni" # "a11y", "omni", "mixed-omni", "oss", "mixed-oss"
som_config=None
temparature=1

screen_width = 1920
screen_height = 1200
headless = False
observation_type = "screenshot_a11y_tree" # "a11y_tree", "screenshot_a11y_tree", "som"
emulator_ip = "127.0.0.1" # Server2 on computer ["windows VM in docker" or "windows VM"]
emulator_port = 5050 # Server2 on computer ["windows VM in docker" or "windows VM"]
a11y_backend = "uia" # "uia" or "win32"

test_config_base_dir = "configs"
domain = "notepad"
example_id = "366de66e-cbae-4d72-b042-26390db2b145-WOS"


# Arguments
class Args:
    pass

args = Args()
args.sleep_after_execution = 3


# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------

agent = NaviAgent(
            server=server,
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
        a11y_backend=a11y_backend,
        emulator_ip=emulator_ip, #for OS running on docker
        emulator_port=emulator_port, #for OS running on docker
    )

config_file = os.path.join(test_config_base_dir, f"examples/{domain}/{example_id}.json")
with open(config_file, "r", encoding="utf-8") as f:
    example = json.load(f)

instruction = example["instruction"]
max_steps = 15
scores = []
example_result_dir = os.path.join(test_config_base_dir, f"results/{domain}/{example_id}")
os.makedirs(example_result_dir, exist_ok=True)





# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------
def run_single_example(agent, env, example, max_steps, instruction, args, example_result_dir, scores):
    agent.reset()
    obs = env.reset(task_config=example)
    done = False
    step_idx = 0

    #env.controller.start_recording()
    start_time = datetime.datetime.now()
    
    # Initialize recorder, which will save the trajectory as a JSON & HTML in {example_result_dir}/traj.(jsonl,html)
    recorder = TrajectoryRecorder(example_result_dir)
    
    # Record initial state
    init_timestamp = start_time.strftime("%Y%m%d@%H%M%S")
    recorder.record_init(obs, example, init_timestamp)
    
    while not done and step_idx < max_steps:
        if obs is None:
            logger.error("Observation is None. Waiting a little to do next step.")
            time.sleep(5)
            step_idx += 1
            continue

        logger.info("Agent: Thinking...")
        try:
            response, actions, logs, computer_update_args = agent.predict(
                instruction,
                obs
            )
        except Exception as e:
            logger.error("Error in agent predict: %s", e)
            logger.error(traceback.format_exc())
            break

        # update the computer object, used by navi's action space
        if computer_update_args:
            env.controller.update_computer(**computer_update_args)
        
        # step environment with agent actions 
        for action in actions:
            # Capture the timestamp before executing the action
            action_timestamp = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")
            elapsed_timestamp = f"{datetime.datetime.now() - start_time}"
            logger.info("Step %d: %s", step_idx + 1, action)
            
            obs, reward, done, info = env.step(action, args.sleep_after_execution)

            logger.info("Reward: %.2f", reward)
            logger.info("Done: %s", done)
            
            # Record step data
            recorder.record_step(
                obs, 
                logs,
                step_idx,
                action_timestamp,
                elapsed_timestamp,
                action,
                reward,
                done,
                info
            )

            if done:
                logger.info("The episode is done.")
                break
        # inc step counter
        step_idx += 1
    
    logger.info("Running evaluator(s)...")
    result = env.evaluate()
    logger.info("Result: %.2f", result)
    scores.append(result)

    with open(os.path.join(example_result_dir, "result.txt"), "w", encoding="utf-8") as f:
        f.write(f"{result}\n")
    
    # Record final results
    recorder.record_end(result, start_time)
    # env.controller.end_recording(os.path.join(example_result_dir, "recording.mp4"))
# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------
# Run example

try:
    run_single_example(
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
