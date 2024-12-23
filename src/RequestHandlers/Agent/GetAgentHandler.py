from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, Agent
from typing import Optional


def get_agent_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Agent.Agent:
    # Get the path parameters
    agent_id = lambda_event.requestParameters.get("agent_id")
    if ( not agent_id):
        raise Exception("agent_id is required", 400)
    agent = None
    if (user):
        dbUser = User.get_user(user.sub)
        agent = Agent.get_agent_for_user(agent_id, dbUser)
    else:
        agent = Agent.get_public_agent(agent_id)
    return agent