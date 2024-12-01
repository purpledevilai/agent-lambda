from Models.Context import get_context_for_user, create_context
from Models.Agent import get_agent_for_orgs, get_public_agent
from Models.User import get_user
from Services.ContextInvoke import context_invoke

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

def get_context_handler(context_id, agent_id, user_id, invoke_agent_message):   
    if (context_id):
        context = get_context_for_user(context_id, user_id)
        return transform_context_for_frontend(context)
    
    if (agent_id == None):
        agent_id = "default-agent-1"

    agent = None
    if user_id == None:
        agent = get_public_agent(agent_id)
    else:
        user = get_user(user_id)
        agent = get_agent_for_orgs(agent_id, user["organizations"])

    context = create_context(agent["agent_id"], user_id)

    if (invoke_agent_message):
        context = context_invoke(context, agent)

    return transform_context_for_frontend(context)


    


            