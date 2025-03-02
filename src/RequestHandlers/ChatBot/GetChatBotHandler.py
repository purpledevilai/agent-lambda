from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ChatPage, Agent, User
from RequestHandlers.ChatBot.ChatBotJsTemplate import chat_bot_js_template

def get_chat_bot_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> str:
    # Get the path parameters
    chat_page_id = lambda_event.requestParameters.get("chat_page_id")
    if not chat_page_id:
        raise Exception("chat_page_id is required", 400)
    
    # Get chat page
    chat_page = ChatPage.get_chat_page(chat_page_id)
    if not chat_page:
        raise Exception("Chat page not found", 404)

    # Get agent
    agent = None
    if (user):
        dbUser = User.get_user(user.sub)
        agent = Agent.get_agent_for_user(chat_page.agent_id, dbUser)
    else:
        agent = Agent.get_public_agent(chat_page.agent_id)

    # Prep chat box string javascript string
    chat_bot_js = chat_bot_js_template.replace("{", "{{").replace("}", "}}").replace("<%", "{").replace("%>", "}")

    # format chat box string
    chat_bot_js = chat_bot_js.format(
        agent_id=agent.agent_id,
        agent_speaks_first="true" if agent.agent_speaks_first else "false",
        header_title=chat_page.heading,
        chat_button_title="💬 Chat",
        primary_color=chat_page.chat_page_style.background_color,
        bot_message_color="#d3d3d3",
        bot_text_color="#3c3c3c",
        user_message_color=chat_page.chat_page_style.background_color,
        user_text_color=chat_page.chat_page_style.heading_color,
        chat_background_color="white",
        chat_border_color="rgba(0,0,0,0.2)",
        input_text_color="black",
        input_background_color="white"
    )

    return chat_bot_js

    