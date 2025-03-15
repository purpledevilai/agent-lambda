import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Tool, User
from Models import ParameterDefinition

def update_tool_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Tool.Tool:   
    
    # Get the body of the request
    body = Tool.UpdateToolParams(**json.loads(lambda_event.body))

    # Get the tool
    tool_id = lambda_event.requestParameters.get("tool_id")
    if ( not tool_id):
        raise Exception("tool_id is required", 400)
    
    # Get the user
    dbUser = User.get_user(user.sub)

    # Get the tool
    tool = Tool.get_tool_for_user(tool_id, dbUser)

    # Check that user has access to the parameter definition
    if (body.pd_id):
        ParameterDefinition.get_parameter_definition_for_user(body.pd_id, dbUser)

    # Update the tool
    update_dict = {k: v for k, v in body.model_dump().items() if v is not None}
    update_dict["pd_id"] = body.pd_id # Explicitly set pd_id if it is None
    tool_dict = tool.model_dump()
    tool_dict.update(update_dict)
    update_tool = Tool.Tool(**tool_dict)

    Tool.save_tool(update_tool)

    return update_tool


    


            