from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import ChatPage, Agent, User
from src.RequestHandlers.ChatBot.ChatBotJsTemplate import chat_bot_js_template

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
        bot_message_color=chat_page.chat_box_style.ai_message_background_color,
        bot_text_color=chat_page.chat_box_style.ai_message_text_color,
        user_message_color=chat_page.chat_box_style.user_message_background_color,
        user_text_color=chat_page.chat_box_style.user_message_text_color,
        chat_background_color=chat_page.chat_box_style.background_color,
        chat_border_color=chat_page.chat_box_style.border_color,
        input_text_color=chat_page.chat_box_style.user_input_textarea_text_color,
        input_background_color=chat_page.chat_box_style.user_input_background_color
    )

    return chat_bot_js

    