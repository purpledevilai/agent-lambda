from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ChatPage, User, SuccessResponse

def delete_chat_page_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse.SuccessResponse:
    chat_page_id = lambda_event.requestParameters.get("chat_page_id")
    if not chat_page_id:
        raise Exception("chat_page_id is required", 400)
    dbUser = User.get_user(user.sub)
    chat_page = ChatPage.get_chat_page(chat_page_id)
    if chat_page.org_id not in dbUser.organizations:
        raise Exception("User does not have access to this chat page", 403)
    ChatPage.delete_chat_page(chat_page.chat_page_id)
    return SuccessResponse.SuccessResponse(**{
        "success": True
   })