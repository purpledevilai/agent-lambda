from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, Integration


def get_integration_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Integration.Integration:
    integration_id = lambda_event.requestParameters.get("integration_id")
    if not integration_id:
        raise Exception("integration_id is required", 400)
    db_user = User.get_user(user.sub)
    return Integration.get_integration_for_user(integration_id, db_user)
