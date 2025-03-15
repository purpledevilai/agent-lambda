import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Tool, User
from Models import ParameterDefinition

def create_tool_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Tool.Tool:   
    
    dbUser = User.get_user(user.sub)

    # Get the body of the request
    body = Tool.CreateToolParams(**json.loads(lambda_event.body))
    if (body.org_id == None):
        body.org_id = dbUser.organizations[0]
    elif (body.org_id not in dbUser.organizations):
        raise Exception("User does not have access to this organization", 403)
    
    # Validate user has access to the parameter definition
    if (body.pd_id):
        ParameterDefinition.get_parameter_definition_for_user(body.pd_id, dbUser)

    # Create the tool
    tool = Tool.create_tool(
        org_id=body.org_id,
        name=body.name,
        description=body.description,
        pd_id=body.pd_id,
        code=body.code,
    )

    return tool


    


            