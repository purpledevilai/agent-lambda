from AWS.Lambda import LambdaEvent
from AWS.Cognito import delete_user_from_cognito, CognitoUser
from Models.User import get_user, delete_user, User
from Models.SuccessResponse import SuccessResponse
from Models.Context import delete_all_contexts_for_user
from Models.Organization import remove_user_from_organization, delete_organization, Organization

def delete_user_handler(lambda_event: LambdaEvent, user: CognitoUser) -> User:
    # Get the user
    user = get_user(user.sub)

    # Delete all contexts
    delete_all_contexts_for_user(user.user_id)

    # Remove user from thier organizations
    for org_id in user.organizations:
        organization: Organization = remove_user_from_organization(org_id, user.user_id)
        if len(organization.users) == 0:
            # If they were the only user in the org, delete the org
            delete_organization(org_id)

    # Detete the user
    delete_user(user.user_id)

    # Delete the user from cognito
    delete_user_from_cognito(user.user_id)

    return SuccessResponse(success=True)