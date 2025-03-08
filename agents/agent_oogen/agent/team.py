from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMessageTermination, HandoffTermination
from autogen_agentchat.base import Handoff
from agent.agent_me import OOMeAgent
from tracker import Tracker
from config import OOConfig 
import logging

logger = logging.getLogger("agent.team")

def init_team(config: OOConfig, tracker: Tracker) -> RoundRobinGroupChat:
    logger.debug("Initializing team...")

    # Agent
    agent_me = OOMeAgent(
        config=config, 
        tracker=tracker,
        handoffs=[Handoff(target="user", message="Transfer to user.")],
    )

    handoff_termination = HandoffTermination(target="user")
    text_termination = TextMessageTermination(agent_me.name)

    # Team 
    team = RoundRobinGroupChat(
            [agent_me],
            termination_condition=text_termination | handoff_termination,
        )
    return team