from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models.User import get_user
from Models.Organization import get_organization
from pydantic import BaseModel

class GetUserOrg(BaseModel):
    id: str
    name: str

class GetUserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    organizations: list[GetUserOrg]

def get_user_handler(lambda_event: LambdaEvent, user: CognitoUser) -> GetUserResponse:
    # User
    dbUser = get_user(user.sub)

    def get_filtered_organization(org_id):
        org = get_organization(org_id)
        return {
            "id": org.org_id,
            "name": org.name,
        }

    return GetUserResponse(**{
        "id": user.sub,
        "email": user.email,
        "first_name": user.given_name,
        "last_name": user.family_name,
        "organizations": [
            get_filtered_organization(org_id)
            for org_id in dbUser.organizations
        ],
    })