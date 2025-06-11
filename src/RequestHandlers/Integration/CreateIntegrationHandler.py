import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Integration, User


def create_integration_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Integration.Integration:
    db_user = User.get_user(user.sub)
    body = Integration.CreateIntegrationParams(**json.loads(lambda_event.body))
    if body.org_id is None:
        body.org_id = db_user.organizations[0]
    elif body.org_id not in db_user.organizations:
        raise Exception("User does not have access to this organization", 403)

    integration = Integration.create_integration(
        org_id=body.org_id,
        type=body.type,
        integration_config=body.integration_config,
    )
    return integration
