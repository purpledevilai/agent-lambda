import os
from datetime import datetime
import uuid
from src.AWS.DynamoDB import get_item, put_item, get_all_items_by_index

AGENTS_TABLE_NAME = os.environ["AGENTS_TABLE_NAME"]
AGENTS_PRIMARY_KEY = os.environ["AGENTS_PRIMARY_KEY"]


def agent_exists(agent_id: str) -> bool:
    try:
        get_item(AGENTS_TABLE_NAME, AGENTS_PRIMARY_KEY, agent_id)
        return True
    except:
        return False


def create_agent(agent_name: str, prompt: str, user_id: str, org_id: str, is_public: bool, agent_description: str) -> dict:
    agent = {
        AGENTS_PRIMARY_KEY: str(uuid.uuid4()),
        "agent_name": agent_name,
        "prompt": prompt,
        "user_id": user_id,
        "org_id": org_id,
        "is_public": is_public,
        "agent_description": agent_description,
        "is_default_agent": False,
        "created_at": int(datetime.timestamp(datetime.now())),
    }
    put_item(AGENTS_TABLE_NAME, agent)
    return agent

def update_agent(agent_id: str, agent_name: str, prompt: str, is_public: bool, agent_description: str) -> dict:
    agent = get_agent(agent_id)
    if agent.get("is_default_agent"):
        raise Exception("Cannot update default agent")
    if agent_name != None:
        agent["agent_name"] = agent_name
    if prompt != None:
        agent["prompt"] = prompt
    if is_public != agent.get("is_public"):
        agent["is_public"] = is_public
    if agent_description != None:
        agent["agent_description"] = agent_description
    put_item(AGENTS_TABLE_NAME, agent)
    return agent


def get_agent(agent_id: str) -> dict:
    try:
        return get_item(AGENTS_TABLE_NAME, AGENTS_PRIMARY_KEY, agent_id)
    except:
        raise Exception(f"Agent with id: {agent_id} does not exist")


def get_agent_for_user(agent_id: str, user_id: str) -> dict:
    agent = get_agent(agent_id)
    if (agent.get("is_public")):
        return agent
    if (agent.get("user_id") == user_id):
        return agent
    if (agent.get("is_default_agent") and user_id != None):
        return agent
    raise Exception(f"Agent does not belong to user")

def get_agents_in_org(org_id: str):
    return get_all_items_by_index(AGENTS_TABLE_NAME, "org_id", org_id)

def get_public_agent(agent_id: str) -> dict:
    agent = get_agent(agent_id)
    if (agent.get("is_public")):
        return agent
    raise Exception(f"Agent is not public")


def save_agent(agent: dict) -> dict:
    put_item(AGENTS_TABLE_NAME, agent)


def get_default_agents() -> list[dict]:
    return get_all_items_by_index(AGENTS_TABLE_NAME, "user_id", "default")


def get_agents_for_user(user_id: str):
    default_agents = get_default_agents()
    user_agents = get_all_items_by_index(AGENTS_TABLE_NAME, "user_id", user_id)
    return default_agents + user_agents

def get_agent_for_orgs(agent_id: str, org_ids: list[str]):
    agent = get_agent(agent_id)
    if (agent.get("is_public")):
        return agent
    if (agent.get("org_id") == "default"):
        return agent
    if (agent.get("org_id") in org_ids):
        return agent
    raise Exception(f"Agent does not belong to users orgs")
