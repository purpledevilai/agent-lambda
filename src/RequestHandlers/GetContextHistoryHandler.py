from Models.Context import get_contexts_by_user_id
from Models.Agent import get_agent
import json

def transform_context_for_frontend(context):
    return {
        "context_id": context["context_id"],
        "user_id": context["user_id"],
        "last_message": context["messages"][-1]["content"] if len(context["messages"]) > 0 else "",
        "time_stamp": context["time_stamp"],
        "agent": {
            "agent_id": context["agent"]["agent_id"],
            "agent_name": context["agent"]["agent_name"],
            "agent_description": context["agent"]["agent_description"],
        }
    }

def get_context_history(user_id):   
    contexts = get_contexts_by_user_id(user_id)

    agentIds = set()
    for context in contexts:
        agentIds.add(context["agent_id"])

    agents = {}
    for agentId in agentIds:
        agent = get_agent(agentId)
        agents[agentId] = agent

    returnContexts = []
    for context in contexts:
        context["agent"] = agents[context["agent_id"]]
        transformedContext = transform_context_for_frontend(context)
        returnContexts.append(transformedContext)

    return returnContexts


    


            