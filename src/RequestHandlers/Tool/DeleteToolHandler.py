from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Tool, User, SuccessResponse

def delete_tool_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse.SuccessResponse:
    tool_id = lambda_event.requestParameters.get("tool_id")
    if not tool_id:
        raise Exception("tool_id is required", 400)
    dbUser = User.get_user(user.sub)
    tool = Tool.get_tool_for_user(tool_id, dbUser)
    Tool.delete_tool(tool.tool_id)
    return SuccessResponse.SuccessResponse(**{
        "success": True
    })
