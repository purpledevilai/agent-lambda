from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User, SuccessResponse

def delete_agent_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse.SuccessResponse:
    agent_id = lambda_event.requestParameters.get("agent_id")
    if not agent_id:
        raise Exception("agent_id is required", 400)
    dbUser = User.get_user(user.sub)
    agent = Agent.get_agent_for_user(agent_id, dbUser)
    Agent.delete_agent(agent.agent_id)
    return SuccessResponse.SuccessResponse(**{
        "success": True
    })
