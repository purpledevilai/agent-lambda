from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, ParameterDefinition
from typing import Optional


def get_parameter_definition_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> ParameterDefinition.ParameterDefinition:
    # Get the path parameters
    pd_id = lambda_event.requestParameters.get("pd_id")
    if ( not pd_id):
        raise Exception("pd_id is required", 400)
    dbUser = User.get_user(user.sub)
    return ParameterDefinition.get_parameter_definition_for_user(pd_id, dbUser)
