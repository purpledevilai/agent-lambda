import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token, agent_id_outside_of_org
from src.lambda_function import lambda_handler
# Import for test
from src.AWS import Cognito
from src.Models import ChatPage, Agent, Context, User

class TestChatBot(unittest.TestCase):

    # Helper variables
    chat_page_style = {
        "background_color": "#FFFFFF",
        "heading_color": "#000000",
        "description_color": "#000000",
        "button_background_color": "#000000",
        "button_text_color": "#FFFFFF",
        "button_hover_background_color": "#FFFFFF",
        "button_hover_text_color": "#000000"
    }

    chat_box_style = {
        "background_color": "#FFFFFF",
        "border_color": "#000000",
        "ai_message_background_color": "#000000",
        "ai_message_text_color": "#FFFFFF",
        "user_message_background_color": "#000000",
        "user_message_text_color": "#FFFFFF",
        "user_input_background_color": "#000000",
        "user_input_textarea_background_color": "#000000",
        "user_input_textarea_text_color": "#FFFFFF",
        "user_input_textarea_focus_color": "#000000",
        "user_input_textarea_placeholder_text": "Placeholder",
        "user_input_textarea_placeholder_color": "#000000",
        "user_input_send_button_color": "#FFFFFF",
        "user_input_send_button_hover_color": "#000000",
        "user_input_send_button_text_color": "#000000",
        "typing_indicator_background_color": "#FFFFFF",
        "typing_indicator_dot_color": "#000000"
    }

    buttons = [
        {
            "label": "Test Button",
            "link": "https://www.google.com"
        }
    ]

    def test_get_chat_bot(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent: Agent.Agent = Agent.create_agent(
            agent_name="Test Agent",
            agent_description="Test Description",
            prompt="Test Prompt",
            org_id=user.organizations[0],
            is_public=False,
            agent_speaks_first=False,
        )
        chat_page = ChatPage.create_chat_page(ChatPage.CreateChatPageParams(**{
            "agent_id": agent.agent_id,
            "org_id": user.organizations[0],
            "heading": "Test Heading",
            "description": "Test Description",
            "chat_page_style": self.chat_page_style,
            "chat_box_style": self.chat_box_style,
            "buttons": self.buttons
        }))

        # Create request
        request = create_request(
            method="GET",
            path=f"/chat-bot/{chat_page.chat_page_id}",
            headers={
                "Authorization": access_token
            },
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        print(res_body)
        
        # Clean up
        ChatPage.delete_chat_page(chat_page.chat_page_id)
        Agent.delete_agent(agent.agent_id)