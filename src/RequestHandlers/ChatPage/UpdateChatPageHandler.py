import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ChatPage, Agent, User

def update_chat_page_handler(lambda_event: LambdaEvent, user: CognitoUser) -> ChatPage.ChatPage:   
    
    db_user = User.get_user(user.sub)

    # Get the body of the request
    body = ChatPage.UpdateChatPageParams(**json.loads(lambda_event.body))

    # Get the chat page
    chat_page_id = lambda_event.requestParameters.get("chat_page_id")
    if ( not chat_page_id):
        raise Exception("chat_page_id is required", 400)
    
    # Get the chat page
    chat_page = ChatPage.get_chat_page(chat_page_id)
    if (chat_page.org_id not in db_user.organizations):
        raise Exception("User does not have access to this organization", 403)
    
    if (body.agent_id):
        # Agent - will throw exception if user does not have access
        Agent.get_agent_for_user(body.agent_id, db_user)

    # Update the chat page
    update_dict = {k: v for k, v in body.model_dump().items() if v is not None}
    chat_page_dict = chat_page.model_dump()
    chat_page_dict.update(update_dict)
    update_chat_page = ChatPage.ChatPage(**chat_page_dict)

    ChatPage.save_chat_page(update_chat_page)

    return update_chat_page