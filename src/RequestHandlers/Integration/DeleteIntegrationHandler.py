from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Integration, User, SuccessResponse


def delete_integration_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse.SuccessResponse:
    integration_id = lambda_event.requestParameters.get("integration_id")
    if not integration_id:
        raise Exception("integration_id is required", 400)
    db_user = User.get_user(user.sub)
    Integration.get_integration_for_user(integration_id, db_user)
    Integration.delete_integration(integration_id)
    return SuccessResponse.SuccessResponse(success=True)
