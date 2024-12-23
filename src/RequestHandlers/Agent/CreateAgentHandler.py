import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User

def create_agent_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Agent.Agent:   
    
    dbUser = User.get_user(user.sub)

    # Get the body of the request
    body = Agent.CreateAgentParams(**json.loads(lambda_event.body))
    if (body.org_id == None):
        body.org_id = dbUser.organizations[0]

    # Create the agent
    agent = Agent.create_agent(
        agent_name=body.agent_name,
        agent_description=body.agent_description,
        prompt=body.prompt,
        org_id=body.org_id,
        is_public=body.is_public,
        agent_speaks_first=body.agent_speaks_first,
        tools=body.tools
    )

    return agent


    


            