from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, SingleMessageEndpoint as SME
from pydantic import BaseModel

class GetSMEsResponse(BaseModel):
    smes: list[SME.SingleMessageEndpoint]


def get_smes_handler(lambda_event: LambdaEvent, user: CognitoUser) -> GetSMEsResponse:
    # Get user object
    user = User.get_user(user.sub)

    # Ensure user has at least one organization
    if len(user.organizations) == 0:
        raise Exception("User is not a member of any organizations", 400)

    # Parse org_id from query params
    org_id = None
    if lambda_event.queryStringParameters is not None:
        org_id = lambda_event.queryStringParameters.get("org_id")

    if org_id is None:
        org_id = user.organizations[0]
    elif org_id not in user.organizations:
        raise Exception("User is not a member of the specified organization", 403)

    # Fetch SMEs for the organization
    smes = SME.get_smes_for_org(org_id)

    return GetSMEsResponse(smes=smes)
