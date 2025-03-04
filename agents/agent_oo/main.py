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
from dotenv import load_dotenv
load_dotenv()

from trajectory_recorder import TrajectoryRecorder
from agent.main import OOAgent
from environment.computer.env import ComputerEnv

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

model="gpt-4o"
temparature=1

emulator_ip = "127.0.0.1" # Server2 on computer ["windows VM in docker" or "windows VM"]
emulator_port = 5050 # Server2 on computer ["windows VM in docker" or "windows VM"]

config_base_dir = "configs"
results_base_dir = "results"
domain = "notepad"
example_id = "366de66e-cbae-4d72-b042-26390db2b145-WOS"


# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------

# TODO:
# Optimize the action_space !!

agent = OOAgent(
            model=model,
            temperature=temparature
        )

env = ComputerEnv(
        action_space=agent.action_space,
        emulator_ip=emulator_ip, 
        emulator_port=emulator_port, 
    )

config_file_path = os.path.join(config_base_dir, domain, f"{example_id}.json")
with open(config_file_path, "r", encoding="utf-8") as f:
    config_file = json.load(f)

max_steps = 15
scores = []
result_path = os.path.join(results_base_dir, domain, example_id)
os.makedirs(result_path, exist_ok=True)


# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------
def run(agent, env, config, max_steps, result_dir, scores):
    agent.reset()
    obs = env.reset(task_config=config)
    done = False
    step_idx = 0

    #env.controller.start_recording()
    start_time = datetime.datetime.now()
    
    # Initialize recorder, which will save the trajectory as a JSON & HTML in {example_result_dir}/traj.(jsonl,html)
    recorder = TrajectoryRecorder(result_dir)
    
    # Record initial state
    init_timestamp = start_time.strftime("%Y%m%d@%H%M%S")
    recorder.record_init(obs, config, init_timestamp)
    
    while not done and step_idx < max_steps:
        if obs is None:
            logger.error("Observation is None. Waiting a little to do next step.")
            time.sleep(5)
            step_idx += 1
            continue

        logger.info("Agent: Thinking...")
        try:
            response, actions, logs, computer_update_args = agent.predict(
                config["instruction"],
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
            
            obs, reward, done, info = env.step(action)

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

    with open(os.path.join(result_dir, "result.txt"), "w", encoding="utf-8") as f:
        f.write(f"{result}\n")
    
    # Record final results
    recorder.record_end(result, start_time)
# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------
try:
    run(
        agent, 
        env, 
        config_file, 
        max_steps, 
        result_path,
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
