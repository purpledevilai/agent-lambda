from AWS.Lambda import LambdaEvent
from AWS import Cognito
from Models.SuccessResponse import SuccessResponse
from Models import User
from Models import Context
from Models import Organization

def delete_user_handler(lambda_event: LambdaEvent, user: Cognito.CognitoUser) -> User.User:
    # Get the user
    user = User.get_user(user.sub)

    # Delete all contexts
    Context.delete_all_contexts_for_user(user.user_id)

    # Remove user from thier organizations
    for org_id in user.organizations:
        organization: Organization = Organization.remove_user_from_organization(org_id, user.user_id)
        if len(organization.users) == 0:
            # If they were the only user in the org, delete the org
            Organization.delete_organization(org_id)

    # Detete the user
    User.delete_user(user.user_id)

    # Delete the user from cognito
    Cognito.delete_user_from_cognito(user.user_id)

    return SuccessResponse(success=True)