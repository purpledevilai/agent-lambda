from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ParameterDefinition, User, SuccessResponse

def delete_parameter_definition_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse.SuccessResponse:
    pd_id = lambda_event.requestParameters.get("pd_id")
    if not pd_id:
        raise Exception("pd_id is required", 400)
    dbUser = User.get_user(user.sub)
    parameter_definition = ParameterDefinition.get_parameter_definition_for_user(pd_id, dbUser)
    ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)
    return SuccessResponse.SuccessResponse(**{
        "success": True
    })
