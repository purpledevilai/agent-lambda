import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
# Imports for the test
from src.AWS import Cognito
from src.Models import Context, User, Agent

class TestChat(unittest.TestCase):

    def test_chat(self):

        # Set up
        user = Cognito.get_user_from_cognito(access_token)
        context = Context.create_context("aj", user.sub)

        # Create the request
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hello"
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda function
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        self.assertIn("response", response)

        # Clean up
        Context.delete_context(context.context_id)

    def test_public_chat(self):
        
        # Set up
        context = Context.create_context("aj-public", None)

        # Create the request
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hello"
            }
        )

        # Call the lambda function
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        self.assertIn("response", response)

        # Clean up
        Context.delete_context(context.context_id)

    def test_chat_with_function_call(self):

        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="Call the pass_event tool with the type as 'echo' and the data as what the user said",
            tools=[
                "pass_event"
            ]
        )
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Create the request
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hello There!"
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda function
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        print(response)

        # Check check for events in the response
        self.assertIn("events", response)

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_chat_with_adding_ai_message(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="You are a helpful assistant.",
            tools=[]
        )
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Create the request
        request = create_request(
            method="POST",
            path="/chat/add-ai-message",
            body={
                "context_id": context.context_id,
                "message": "Hello, I'm an AI, how can I assist you today?"
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda function
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        print(response)
        self.assertIn("response", response)

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_chat_with_prompting_ai_message(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="You are a helpful assistant.",
            tools=[]
        )
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Add a user message to the context
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hi there my name is Keanu, what is the capital of France?"
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda function
        result = lambda_handler(request, None)

        # Print the result
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        print(response)     

        # Create another request to have the AI reach out with a prompt
        request = create_request(
            method="POST",
            path="/chat/add-ai-message",
            body={
                "context_id": context.context_id,
                "prompt": "You're reaching back out to the user. In your next message, sell them on a new deal on flights to Argentina."
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda function
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        print(response)
        self.assertIn("response", response)

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        
        