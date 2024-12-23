from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, Agent
from pydantic import BaseModel

class GetAgentsResponse(BaseModel):
    agents: list[Agent.Agent]


def get_agents_handler(lambda_event: LambdaEvent, user: CognitoUser):
    # User
    user = User.get_user(user.sub)

    # User must have at least one organization
    if len(user.organizations) == 0:
        raise Exception("User is not a member of any organizations", 400)
    
    # Org ID
    org_id = lambda_event.queryStringParameters.get("org_id")
    if org_id is None:
        org_id = user.organizations[0]
    elif org_id not in user.organizations:
        raise Exception("User is not a member of the specified organization", 403)

    # Org agents
    return GetAgentsResponse(agents=Agent.get_agents_in_org(org_id))