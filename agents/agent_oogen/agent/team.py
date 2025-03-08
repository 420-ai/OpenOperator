from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMessageTermination
from agent.agent_me import OOMeAgent
from tracker import Tracker
import logging

logger = logging.getLogger("agent.team")

def init_team(tracker: Tracker) -> RoundRobinGroupChat:
    logger.debug("Initializing team...")

    # Agent
    agent_me = OOMeAgent(tracker=tracker)

    termination_condition = TextMessageTermination(agent_me.name)

    # Team 
    team = RoundRobinGroupChat(
            [agent_me],
            termination_condition=termination_condition,
        )
    return team