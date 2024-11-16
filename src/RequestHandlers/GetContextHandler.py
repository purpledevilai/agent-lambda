from Agent.Context import get_context_for_user, create_context
from Agent.Agent import get_agent_for_user

def transform_context_for_frontend(context):
    messages = []
    for message in context["messages"]:
        if (message["type"] == "human" or message["type"] == "ai"):
            messages.append({
                "from": message["type"],
                "message": message["content"]
            })
    context["messages"] = messages
    return context

def get_context_handler(context_id, agent_id, user_id):        
    if (context_id):
        context = get_context_for_user(context_id, user_id)
        return transform_context_for_frontend(context)
    
    if (agent_id == None):
        agent_id = "default-agent-1"

    agent = get_agent_for_user(agent_id, user_id)

    context = create_context(agent["agent_id"], user_id)

    return transform_context_for_frontend(context)


    


            