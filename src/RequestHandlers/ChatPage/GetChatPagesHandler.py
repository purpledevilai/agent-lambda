from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ChatPage, User
from pydantic import BaseModel

class GetChatPagesResponse(BaseModel):
    chat_pages: list[ChatPage.ChatPage]

def get_chat_pages_handler(lambda_event: LambdaEvent, user: CognitoUser):
    # User
    user = User.get_user(user.sub)

    # User must have at least one organization
    if len(user.organizations) == 0:
        raise Exception("User is not a member of any organizations", 400)
    
    # Org ID
    org_id = None
    if lambda_event.queryStringParameters is not None:
        org_id = lambda_event.queryStringParameters.get("org_id")
    if org_id is None:
        org_id = user.organizations[0]
    elif org_id not in user.organizations:
        raise Exception("User is not a member of the specified organization", 403)

    # Org chat pages
    return GetChatPagesResponse(chat_pages=ChatPage.get_chat_pages_in_org(org_id))