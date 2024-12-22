from Models.User import get_user
#from Models.Agent import get_agent_for_orgs, create_agent, update_agent

def create_or_update_agent_handler(
        user_id: str,
        org_id: str,
        agent_id: str,
        prompt: str,
        is_public: bool,
        agent_name: str,
        agent_description: str
    ) -> dict:
    return "Need to implement"
    
    # # User permissions
    # user = get_user(user_id)
    # if org_id == None:
    #     org_id = user["organizations"][0]
    # elif org_id not in user["organizations"]:
    #     raise Exception("User does not have permission to create an agent in this organization")
    
    # # Create or update the agent
    # agent = None
    # if agent_id == None:
    #     create_agent_params = {
    #         "agent_name": agent_name,
    #         "prompt": prompt,
    #         "user_id": user_id,
    #         "org_id": org_id,
    #         "is_public": is_public,
    #         "agent_description": agent_description
    #     }
    #     agent = create_agent(**create_agent_params)
    # else:
    #     agent = get_agent_for_orgs(agent_id, [org_id])
    #     update_agent_params = {
    #         "agent_id": agent["agent_id"],
    #         "agent_name": agent_name,
    #         "prompt": prompt,
    #         "is_public": is_public,
    #         "agent_description": agent_description
    #     }
    #     agent = update_agent(**update_agent_params)
    # return agent
        
