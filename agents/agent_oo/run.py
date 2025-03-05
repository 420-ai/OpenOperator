from datetime import datetime
import os
import time
import traceback
from agents.agent_oo.tracker import Tracker
import logging

logger = logging.getLogger("main.run")

def run(agent, env, config, max_steps, result_dir, scores):

    logging.debug("Starting run...")

    agent.reset()
    obs, _ = env.reset(task_config=config)
    done = False
    step_counter = 0

    #env.controller.start_recording()
    start_time = datetime.now()
    
    # Initialize tracker, which will save the agent log as a JSON & HTML in {example_result_dir}/traj.(jsonl,html)
    tracker = Tracker(result_dir)
    tracker.log_init(obs, config, start_time.strftime("%Y%m%d@%H%M%S"))
    
    while not done and step_counter < max_steps:
        step_counter += 1
        print("------------------------------------------------")
        print("------------------------------------------------")
        print("Step: ", step_counter)
        print("------------------------------------------------")
        print("------------------------------------------------")

        if obs is None:
            logger.error("Observation is None. Waiting a little to do next step.")
            time.sleep(5)
            continue

        print("-------------------")
        logger.info("Agent: Starting...")
        try:
            actions, logs, computer_update_args = agent.predict(
                config["instruction"],
                obs
            )

            logger.info("Agent suggests %d actions.", len(actions))
        except Exception as e:
            logger.error("Error in agent predict: %s", e)
            logger.error(traceback.format_exc())
            break

        logger.info("Agent: Done.")
        print("-------------------")


        print("-------------------")
        logger.info("Environment: Starting...")

        # update the computer object, used by navi's action space
        if computer_update_args:
            env.controller.update_computer(**computer_update_args)
        
        # step environment with agent actions 
        action_counter = 0
        for action in actions:
            action_counter += 1
            print("------------------------------------------------")
            print(f"Action: {action_counter}")
            print(action)
            print("------------------------------------------------")
            # Capture the timestamp before executing the action
            action_timestamp = datetime.now().strftime("%Y%m%d@%H%M%S")
            elapsed_timestamp = f"{datetime.now() - start_time}"
            
            obs, reward, done, info = env.step(action)

            logger.info("Reward: %.2f", reward)
            logger.info("Done: %s", done)
            
            # Record step data
            tracker.log_step(
                obs, 
                logs,
                step_counter,
                action_counter,
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
        
        logger.info("Environment: Done.")
        print("-------------------")
    

    print("------------------------------------------------")
    logger.info("Episode finished.")
    print("------------------------------------------------")
    logger.debug("Running evaluator(s)...")
    result = env.evaluate()
    logger.debug("Result: %.2f", result)
    scores.append(result)

    with open(os.path.join(result_dir, "result.txt"), "w", encoding="utf-8") as f:
        f.write(f"{result}\n")
    
    # Record final results
    tracker.log_end(result, start_time)