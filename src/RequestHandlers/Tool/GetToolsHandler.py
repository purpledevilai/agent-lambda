from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, Tool
from pydantic import BaseModel
from Models import Agent

class GetToolsResponse(BaseModel):
    tools: list[Tool.Tool]


def get_tools_handler(lambda_event: LambdaEvent, user: CognitoUser):
    # User
    user = User.get_user(user.sub)

    # User must have at least one organization
    if len(user.organizations) == 0:
        raise Exception("User is not a member of any organizations", 400)
    
    # Org ID
    org_id = None
    if lambda_event.queryStringParameters is not None:
        org_id = lambda_event.queryStringParameters.get("org_id")
    if org_id is None:
        org_id = user.organizations[0]
    elif org_id not in user.organizations:
        raise Exception("User is not a member of the specified organization", 403)
    
    # Agent ID
    agent_id = None
    agent = None
    if lambda_event.queryStringParameters is not None:
        agent_id = lambda_event.queryStringParameters.get("agent_id")
    if agent_id is not None:
        agent = Agent.get_agent_for_user(agent_id, user) # Validate user has access to the agent

    # Org tools
    tools = Tool.get_tools_for_org(org_id)
    if agent is not None:
        # If getting tools for agent also return the default tools it uses
        default_tools = Tool.get_tools_for_org("default")
        agent_default_tools = [tool for tool in default_tools if tool.tool_id in agent.tools]
        tools = [tool for tool in tools if tool.tool_id in agent.tools] + agent_default_tools

    return GetToolsResponse(tools=tools)