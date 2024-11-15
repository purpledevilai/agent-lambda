from Agent.Context import get_context_for_user, create_context
from Agent.Agent import get_agent_for_user

def get_context_handler(context_id, agent_id, user_id):        
    if (context_id):
        return get_context_for_user(context_id, user_id)
    
    if (agent_id == None):
        agent_id = "default-agent-1"

    agent = get_agent_for_user(agent_id, user_id)

    context = create_context(agent["agent_id"], user_id)

    return context


    


            