from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, ParameterDefinition
from pydantic import BaseModel

class GetParameterDefinitionsResponse(BaseModel):
    parameter_definitions: list[ParameterDefinition.ParameterDefinition]


def get_parameter_definitions_handler(lambda_event: LambdaEvent, user: CognitoUser):
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

    # Org parameter_definitions
    return GetParameterDefinitionsResponse(parameter_definitions=ParameterDefinition.get_parameter_definitions_for_org(org_id))