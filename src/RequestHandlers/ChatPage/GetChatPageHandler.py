from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ChatPage

def get_chat_page_handler(lambda_event: LambdaEvent, user: CognitoUser) -> ChatPage.ChatPage:
    chat_page_id = lambda_event.requestParameters.get("chat_page_id")
    if not chat_page_id:
        raise Exception("chat_page_id is required", 400)
    chat_page = ChatPage.get_chat_page(chat_page_id)
    return chat_page