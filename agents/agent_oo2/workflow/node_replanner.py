from core.state import State
from core.tracker import Tracker
from core.clients.llm import LLMClient
from core.models import Message, TextContent, ImageContent
from agent_oo2.helpers import encode_image, resize_and_compress_image, fm

import logging
logger = logging.getLogger("node_replanner")

SYSTEM_MESSAGE = """
You are replanner agent.
"""

USER_MESSAGE = """
For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Your objective was this:
{user_task}

Your original plan was this:
{plan}

You have currently done the follow steps:
{past_steps}

Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan.

Final answer should be formatted as [FINAL ANSWER] + your text
"""

class OOReplannerNode:

    def __init__(self, state: State, tracker: Tracker):
        logger.debug("Initializing...")

        self.name = "node_replanner"
        self.description = "Node responsible for replanning"

        self.config = state.get_config()
        self.state = state
        self.tracker = tracker

        self.llm = LLMClient("azure", model="gpt-4o", deployment="gpt-4o-deployment")

    async def execute(self):
        logger.debug("=================================")
        logger.debug(f"Entity: {self.name}")
        logger.debug("=================================")
        logger.info("Predicting ...")
        

        # Get the user task
        user_task = self.config.instruction

        # Get the plan from state
        plan = self.state.current_plan_data["plan_text"]

        # Get all plan steps results
        all_plan_versions = self.state.get_all_plan_versions_data()
        all_plan_steps_results = []
        for plan_version in all_plan_versions:
            plan_steps_results = plan_version["plan_steps_result"]
            all_plan_steps_results.append(plan_steps_results)

        # Take a screenshot
        screenshot_t2 = self.computer.get_screenshot()

        # Resize and compress the screenshot
        screenshot_t2_resized = resize_and_compress_image(screenshot_t2)
        self.state.save_plan_image(screenshot_t2_resized, "t2.png")

        # Messages
        system_message = Message(role="system", content=SYSTEM_MESSAGE)
        user_message = Message(
            role="user", 
            content=[
                TextContent(type="text", text=USER_MESSAGE.format(
                    user_task=user_task,
                    plan=plan,
                    past_steps=all_plan_steps_results)),
                ImageContent(
                    type="image",        
                    data=encode_image(screenshot_t2_resized),
                    media_type="image/png"
                )
            ]
        )

        # region Log + State + Tracker
        self.tracker.save(self.name, [
            ("system_message", system_message.model_dump()),
            ("user_message", user_message.model_dump()),
            ("screenshot_t2_resized", screenshot_t2_resized)
        ])
        # endregion

        # Call LLM
        result = self.llm.call(
            messages=[
                system_message,
                user_message,
            ]
        )

        # region Log + State + Tracker
        cost = f"Provider: {self.llm.provider}, Model: {self.llm.model}, Total cost: {result.usage.cost}$"
        logger.debug(cost)
        logger.debug(fm(result.message.content))

        self.tracker.save(self.name, [
            ("llm_response", result.message.content),
            ("cost", cost),
        ])
        # endregion

        # -----------------------
        # Should we continue?
        # -----------------------
        if "[FINAL ANSWER]" in result.message.content:
            self.state.save_plan_step_text("ALL DONE")
            return "ALL DONE"
        else:
            self.state.create_new_plan_version()
            self.state.save_plan_text(result.message.content)