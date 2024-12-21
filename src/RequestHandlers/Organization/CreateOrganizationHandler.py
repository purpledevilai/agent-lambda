import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Organization
from Models import User


def create_organization_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Organization.Organization:

    # Get the body of the request
    body = json.loads(lambda_event.body)

    # Check for required params
    if "name" not in body:
        raise Exception("No name provided")
    
    # Create the organization
    organization = Organization.create_organization(body["name"])
    organization = Organization.associate_user_with_organization(organization.org_id, user.sub)
    User.associate_organization_with_user(user.sub, organization.org_id)
    return organization
