from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, StructuredResponseEndpoint as SRE
from pydantic import BaseModel

class GetSREsResponse(BaseModel):
    sres: list[SRE.StructuredResponseEndpoint]


def get_sres_handler(lambda_event: LambdaEvent, user: CognitoUser) -> GetSREsResponse:
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

    # Fetch SREs for the organization
    sres = SRE.get_sres_for_org(org_id)

    return GetSREsResponse(sres=sres)
