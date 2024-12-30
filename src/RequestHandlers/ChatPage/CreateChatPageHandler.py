import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ChatPage, Agent, User

def create_chat_page_handler(lambda_event: LambdaEvent, user: CognitoUser) -> ChatPage.ChatPage:   
    
    db_user = User.get_user(user.sub)

    # Get the body of the request
    body = ChatPage.CreateChatPageParams(**json.loads(lambda_event.body))

    # Org
    if (body.org_id == None):
        body.org_id = db_user.organizations[0]
    elif (body.org_id not in db_user.organizations):
        raise Exception("User does not have access to this organization", 403)
    
    # Agent - will throw exception if user does not have access
    Agent.get_agent_for_user(body.agent_id, db_user)

    # Create the chat page
    chat_page = ChatPage.create_chat_page(body)

    return chat_page


    


            