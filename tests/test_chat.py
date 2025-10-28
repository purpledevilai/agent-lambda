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

    def test_chat_without_saving_messages(self):
        """Test that save_messages=False generates messages but doesn't save them to context"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-no-save",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="Call the pass_event tool with the type as 'test' and the data as 'message_not_saved'",
            tools=[
                "pass_event"
            ]
        )
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Record the initial message count
        initial_message_count = len(context.messages)

        # Create the request with save_ai_messages=False
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Test message",
                "save_ai_messages": False
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda function
        result = lambda_handler(request, None)

        # Check the response status
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        print("Response:", json.dumps(response, indent=2))

        # Verify the response has the required fields
        self.assertIn("response", response)
        self.assertIn("saved_ai_messages", response)
        self.assertIn("generated_messages", response)
        
        # Verify saved_ai_messages is False
        self.assertEqual(response["saved_ai_messages"], False)
        
        # Verify we have a response message
        self.assertIsNotNone(response["response"])
        self.assertIsInstance(response["response"], str)
        
        # Verify we have generated_messages
        self.assertIsInstance(response["generated_messages"], list)
        self.assertGreater(len(response["generated_messages"]), 0)
        
        # Verify generated_messages includes tool calls and responses
        has_tool_call = False
        has_tool_response = False
        has_final_message = False
        
        for msg in response["generated_messages"]:
            if msg.get("type") == "tool_call":
                has_tool_call = True
                # Verify tool call structure
                self.assertIn("tool_call_id", msg)
                self.assertIn("tool_name", msg)
                self.assertEqual(msg["tool_name"], "pass_event")
            elif msg.get("type") == "tool_response":
                has_tool_response = True
                # Verify tool response structure
                self.assertIn("tool_call_id", msg)
                self.assertIn("tool_output", msg)
            elif msg.get("sender") == "ai":
                has_final_message = True
                # Verify final AI message structure
                self.assertIn("message", msg)
        
        # Assert we got all expected message types
        self.assertTrue(has_tool_call, "Should have at least one tool call")
        self.assertTrue(has_tool_response, "Should have at least one tool response")
        self.assertTrue(has_final_message, "Should have final AI message")

        # Fetch the context and verify only the human message was saved (not AI-generated messages)
        updated_context = Context.get_context(context.context_id)
        # Should have initial messages + 1 human message, but NOT the AI-generated messages
        self.assertEqual(len(updated_context.messages), initial_message_count + 1,
                        "Only human message should be saved when save_ai_messages=False")

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        
        