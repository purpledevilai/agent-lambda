from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, Integration
from pydantic import BaseModel


class GetIntegrationsResponse(BaseModel):
    integrations: list[Integration.Integration]


def get_integrations_handler(lambda_event: LambdaEvent, user: CognitoUser) -> GetIntegrationsResponse:
    db_user = User.get_user(user.sub)
    if len(db_user.organizations) == 0:
        raise Exception("User is not a member of any organizations", 400)
    org_id = None
    if lambda_event.queryStringParameters is not None:
        org_id = lambda_event.queryStringParameters.get("org_id")
    if org_id is None:
        org_id = db_user.organizations[0]
    elif org_id not in db_user.organizations:
        raise Exception("User is not a member of the specified organization", 403)
    return GetIntegrationsResponse(integrations=Integration.get_integrations_in_org(org_id))
