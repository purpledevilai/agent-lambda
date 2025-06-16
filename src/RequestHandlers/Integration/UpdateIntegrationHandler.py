import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Integration, User


def update_integration_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Integration.Integration:
    integration_id = lambda_event.requestParameters.get("integration_id")
    if not integration_id:
        raise Exception("integration_id is required", 400)
    db_user = User.get_user(user.sub)
    integration = Integration.get_integration_for_user(integration_id, db_user)
    body = Integration.UpdateIntegrationParams(**json.loads(lambda_event.body))
    if body.type is not None:
        integration.type = body.type
    if body.integration_config is not None:
        integration.integration_config = body.integration_config
    return Integration.save_integration(integration)
