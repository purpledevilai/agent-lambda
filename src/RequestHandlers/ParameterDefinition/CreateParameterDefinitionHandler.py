import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ParameterDefinition, User

def create_parameter_definition_handler(lambda_event: LambdaEvent, user: CognitoUser) -> ParameterDefinition.ParameterDefinition:   
    
    dbUser = User.get_user(user.sub)

    # Get the body of the request
    body = ParameterDefinition.CreateParameterDefinitionParams(**json.loads(lambda_event.body))
    if (body.org_id == None):
        body.org_id = dbUser.organizations[0]
    elif (body.org_id not in dbUser.organizations):
        raise Exception("User does not have access to this organization", 403)

    # Create the parameter_definition
    parameter_definition = ParameterDefinition.create_parameter_definition(
        org_id = body.org_id,
        parameters = body.parameters,
    )

    return parameter_definition


    


            