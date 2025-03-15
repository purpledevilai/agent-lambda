import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User, Tool

def update_agent_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Agent.Agent:   
    
    # Get the body of the request
    body = Agent.UpdateAgentParams(**json.loads(lambda_event.body))

    # Get the agent
    agent_id = lambda_event.requestParameters.get("agent_id")
    if ( not agent_id):
        raise Exception("agent_id is required", 400)
    
    # Get the user
    dbUser = User.get_user(user.sub)

    # Get the agent
    agent = Agent.get_agent_for_user(agent_id, dbUser)

    # Update the agent
    update_dict = {k: v for k, v in body.model_dump().items() if v is not None}
    agent_dict = agent.model_dump()
    agent_dict.update(update_dict)
    if agent_dict.get("tools"):
        Tool.validate_tools_for_user(agent_dict["tools"], dbUser)
    update_agent = Agent.Agent(**agent_dict)

    Agent.save_agent(update_agent)

    return update_agent


    


            