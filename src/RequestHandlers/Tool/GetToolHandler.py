from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, Tool
from typing import Optional


def get_tool_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Tool.Tool:
    # Get the path parameters
    tool_id = lambda_event.requestParameters.get("tool_id")
    if ( not tool_id):
        raise Exception("tool_id is required", 400)
    dbUser = User.get_user(user.sub)
    return Tool.get_tool_for_user(tool_id, dbUser)