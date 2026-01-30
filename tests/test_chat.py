import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
# Imports for the test
from src.AWS import Cognito
from src.Models import Context, User, Agent, Tool, ParameterDefinition

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

    def test_add_ai_message_save_both(self):
        """Test save_system_message=True, save_ai_messages=True (saves both)"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-save-both",
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

        # Add a human message first
        Context.add_human_message(context, "Hello")
        initial_message_count = len(context.messages)

        # Add AI message with prompt, saving both system message and AI response
        request = create_request(
            method="POST",
            path="/chat/add-ai-message",
            body={
                "context_id": context.context_id,
                "prompt": "Respond in a friendly tone",
                "save_system_message": True,
                "save_ai_messages": True
            },
            headers={
                "Authorization": access_token
            }
        )

        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        
        self.assertIn("response", response)
        self.assertEqual(response["saved_ai_messages"], True)
        self.assertGreater(len(response["generated_messages"]), 0)

        # Verify both system message and AI messages were saved
        updated_context = Context.get_context(context.context_id)
        self.assertGreater(len(updated_context.messages), initial_message_count)
        
        # Check that we have a system message with our prompt
        system_messages = [msg for msg in updated_context.messages if msg.get("type") == "system"]
        self.assertGreater(len(system_messages), 0)
        self.assertIn("friendly tone", system_messages[-1].get("content", ""))
        
        # Check that we have an AI message
        ai_messages = [msg for msg in updated_context.messages if msg.get("type") == "ai" and msg.get("content")]
        self.assertGreater(len(ai_messages), 0)

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_add_ai_message_save_system_only(self):
        """Test save_system_message=True, save_ai_messages=False (saves only system message)"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-save-system",
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

        # Add a human message first
        Context.add_human_message(context, "Hello")
        initial_message_count = len(context.messages)

        # Add AI message with prompt, saving only system message
        request = create_request(
            method="POST",
            path="/chat/add-ai-message",
            body={
                "context_id": context.context_id,
                "prompt": "Consider the user is a beginner",
                "save_system_message": True,
                "save_ai_messages": False
            },
            headers={
                "Authorization": access_token
            }
        )

        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        
        self.assertIn("response", response)
        self.assertEqual(response["saved_ai_messages"], False)
        self.assertGreater(len(response["generated_messages"]), 0)

        # Verify only system message was saved (not AI messages)
        updated_context = Context.get_context(context.context_id)
        
        # Should have exactly one more message (the system message)
        self.assertEqual(len(updated_context.messages), initial_message_count + 1)
        
        # Check that the last message is the system message with our prompt
        last_message = updated_context.messages[-1]
        self.assertEqual(last_message.get("type"), "system")
        self.assertIn("beginner", last_message.get("content", ""))
        
        # Verify no new AI messages were added after the initial messages
        ai_messages_after = [msg for msg in updated_context.messages[initial_message_count:] if msg.get("type") == "ai"]
        self.assertEqual(len(ai_messages_after), 0)

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_add_ai_message_temporary_steering(self):
        """Test save_system_message=False, save_ai_messages=True (temporary steering - most powerful use case)"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-temp-steering",
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

        # Add a human message first
        Context.add_human_message(context, "Tell me about Python")
        initial_message_count = len(context.messages)
        
        # Count initial system messages
        initial_system_messages = [msg for msg in context.messages if msg.get("type") == "system"]
        initial_system_count = len(initial_system_messages)

        # Add AI message with prompt for temporary steering
        request = create_request(
            method="POST",
            path="/chat/add-ai-message",
            body={
                "context_id": context.context_id,
                "prompt": "Keep your response under 20 words and be very formal",
                "save_system_message": False,  # Don't save the prompt
                "save_ai_messages": True  # Save the AI response
            },
            headers={
                "Authorization": access_token
            }
        )

        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        
        self.assertIn("response", response)
        self.assertEqual(response["saved_ai_messages"], True)
        self.assertGreater(len(response["generated_messages"]), 0)

        # Verify AI messages were saved but system message was NOT saved
        updated_context = Context.get_context(context.context_id)
        self.assertGreater(len(updated_context.messages), initial_message_count)
        
        # Verify the system message was NOT added (count should be the same)
        final_system_messages = [msg for msg in updated_context.messages if msg.get("type") == "system"]
        self.assertEqual(len(final_system_messages), initial_system_count)
        
        # Verify the temporary prompt is NOT in any system message
        for msg in updated_context.messages:
            if msg.get("type") == "system":
                self.assertNotIn("20 words", msg.get("content", ""))
                self.assertNotIn("very formal", msg.get("content", ""))
        
        # Verify AI response WAS saved
        ai_messages_after = [msg for msg in updated_context.messages[initial_message_count:] if msg.get("type") == "ai" and msg.get("content")]
        self.assertGreater(len(ai_messages_after), 0)
        
        print(f"Temporary steering test - AI response: {response['response']}")

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_add_ai_message_save_nothing(self):
        """Test save_system_message=False, save_ai_messages=False (full preview mode)"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-save-nothing",
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

        # Add a human message first
        Context.add_human_message(context, "What's the weather like?")
        # Refresh context from DB to get accurate count
        context = Context.get_context(context.context_id)
        initial_message_count = len(context.messages)

        # Add AI message with prompt, saving nothing (full preview)
        request = create_request(
            method="POST",
            path="/chat/add-ai-message",
            body={
                "context_id": context.context_id,
                "prompt": "Respond with technical meteorological details",
                "save_system_message": False,
                "save_ai_messages": False
            },
            headers={
                "Authorization": access_token
            }
        )

        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        
        self.assertIn("response", response)
        self.assertEqual(response["saved_ai_messages"], False)
        self.assertGreater(len(response["generated_messages"]), 0)

        # Verify NOTHING was saved to the context
        updated_context = Context.get_context(context.context_id)
        self.assertEqual(len(updated_context.messages), initial_message_count)
        
        # Verify no system message was added
        no_new_system = True
        for msg in updated_context.messages[initial_message_count:]:
            if msg.get("type") == "system" and "meteorological" in msg.get("content", ""):
                no_new_system = False
        self.assertTrue(no_new_system)
        
        # Verify no AI message was added after initial messages
        no_new_ai = True
        for msg in updated_context.messages[initial_message_count:]:
            if msg.get("type") == "ai":
                no_new_ai = False
        self.assertTrue(no_new_ai)
        
        print(f"Full preview mode - generated response: {response['response']}")
        print(f"Context unchanged - message count: {len(updated_context.messages)}")

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

    def test_invoke_after_adding_messages(self):
        """Test invoking the agent after manually adding messages via add-messages endpoint"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-invoke-after-add",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="You are a helpful assistant. Respond briefly.",
            tools=[]
        )
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Step 1: Manually add messages to the context
        messages_to_add = [
            {
                "sender": "human",
                "message": "What is 2+2?"
            }
        ]

        add_request = create_request(
            method="POST",
            path="/context/add-messages",
            body={
                "context_id": context.context_id,
                "messages": messages_to_add
            },
            headers={
                "Authorization": access_token
            }
        )

        add_result = lambda_handler(add_request, None)
        self.assertEqual(add_result["statusCode"], 200)

        # Step 2: Invoke the agent to generate a response
        invoke_request = create_request(
            method="POST",
            path="/chat/invoke",
            body={
                "context_id": context.context_id,
                "save_ai_messages": True
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the invoke handler - this should not fail
        invoke_result = lambda_handler(invoke_request, None)
        
        # Check the response
        self.assertEqual(invoke_result["statusCode"], 200)
        invoke_response = json.loads(invoke_result["body"])
        
        # Verify we got a response
        self.assertIn("response", invoke_response)
        self.assertIsNotNone(invoke_response["response"])
        self.assertGreater(len(invoke_response["response"]), 0)
        
        # Verify generated messages
        self.assertIn("generated_messages", invoke_response)
        self.assertGreater(len(invoke_response["generated_messages"]), 0)

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_invoke_after_adding_messages_with_tool_calls(self):
        """Test invoking the agent after manually adding messages with tool calls"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-invoke-with-tools",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="You are a helpful assistant with access to pass_event tool. Continue the conversation naturally.",
            tools=["pass_event"]
        )
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Step 1: Manually add a conversation with tool calls
        messages_to_add = [
            {
                "sender": "human",
                "message": "Can you send an event for me?"
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_123",
                "tool_name": "pass_event",
                "tool_input": {
                    "type": "test_event",
                    "data": "test_data"
                }
            },
            {
                "type": "tool_response",
                "tool_call_id": "call_123",
                "tool_output": "Event of type test_event added!"
            },
            {
                "sender": "ai",
                "message": "I've sent the event for you!"
            },
            {
                "sender": "human",
                "message": "Great! Can you tell me more about what you can do?"
            }
        ]

        add_request = create_request(
            method="POST",
            path="/context/add-messages",
            body={
                "context_id": context.context_id,
                "messages": messages_to_add
            },
            headers={
                "Authorization": access_token
            }
        )

        add_result = lambda_handler(add_request, None)
        self.assertEqual(add_result["statusCode"], 200)
        add_response = json.loads(add_result["body"])
        print("Added messages:", json.dumps(add_response, indent=2))

        # Verify messages were added correctly
        self.assertIn("messages", add_response)
        
        # Step 2: Invoke the agent to respond to the last human message
        invoke_request = create_request(
            method="POST",
            path="/chat/invoke",
            body={
                "context_id": context.context_id,
                "save_ai_messages": True
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the invoke handler - this should not fail even with tool calls in history
        invoke_result = lambda_handler(invoke_request, None)
        
        # Check the response
        self.assertEqual(invoke_result["statusCode"], 200)
        invoke_response = json.loads(invoke_result["body"])
        print("Invoke response:", json.dumps(invoke_response, indent=2))
        
        # Verify we got a response
        self.assertIn("response", invoke_response)
        self.assertIsNotNone(invoke_response["response"])
        self.assertGreater(len(invoke_response["response"]), 0)
        
        # Verify generated messages
        self.assertIn("generated_messages", invoke_response)
        self.assertGreater(len(invoke_response["generated_messages"]), 0)
        
        # Verify saved_ai_messages is True
        self.assertEqual(invoke_response["saved_ai_messages"], True)

        # Step 3: Verify the complete conversation is in the context
        final_context = Context.get_context(context.context_id)
        # Should have all the added messages + the newly generated response
        self.assertGreater(len(final_context.messages), len(messages_to_add))
        
        # Verify the context can be retrieved with tool calls shown
        filtered_context = Context.transform_to_filtered_context(final_context, show_tool_calls=True)
        
        # Count message types
        human_msgs = [m for m in filtered_context.messages if hasattr(m, 'sender') and m.sender == 'human']
        ai_msgs = [m for m in filtered_context.messages if hasattr(m, 'sender') and m.sender == 'ai']
        tool_calls = [m for m in filtered_context.messages if hasattr(m, 'type') and m.type == 'tool_call']
        tool_responses = [m for m in filtered_context.messages if hasattr(m, 'type') and m.type == 'tool_response']
        
        # Verify we have the expected message types
        self.assertGreaterEqual(len(human_msgs), 2, "Should have at least 2 human messages")
        self.assertGreaterEqual(len(ai_msgs), 2, "Should have at least 2 AI messages")
        self.assertGreaterEqual(len(tool_calls), 1, "Should have at least 1 tool call from the manually added messages")
        self.assertGreaterEqual(len(tool_responses), 1, "Should have at least 1 tool response from the manually added messages")

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_additional_agent_tools_with_add_ai_message(self):
        """Test creating a tool, adding it via additional_agent_tools, and invoking via AddAIMessage"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        
        # Create parameter definition for the tool
        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "message",
                    "description": "The message to echo back",
                    "type": "string",
                    "parameters": []
                }
            ]
        )
        
        # Create a simple tool that returns a specific message
        tool_code = '''
def test_echo_tool(message):
    return f"Tool received: {message}"
'''
        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="test_echo_tool",
            description="A test tool that echoes a message",
            code=tool_code,
            pd_id=pd.pd_id,
            pass_context=False,
            is_async=False
        )
        
        # Create an agent without the tool (we'll add it via additional_agent_tools)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-additional-tools",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="You are a helpful assistant. When asked to use a tool, call the test_echo_tool with the message provided.",
            tools=[]
        )
        
        # Create a context with the tool in additional_agent_tools
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id,
            additional_agent_tools=[tool.tool_id]
        )
        
        # Call AddAIMessage with a prompt to call the tool, using terminating_config
        request = create_request(
            method="POST",
            path="/chat/add-ai-message",
            body={
                "context_id": context.context_id,
                "prompt": "Call the test_echo_tool with the message 'Hello from test!'",
                "terminating_config": {
                    "tool_ids": [tool.tool_id],
                    "consecutive_nudges": 2,
                    "max_invocations": 10
                }
            },
            headers={
                "Authorization": access_token
            }
        )
        
        result = lambda_handler(request, None)
        
        # Check the response
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        print("Response:", json.dumps(response, indent=2))
        
        # Verify the response contains the tool's output
        self.assertIn("response", response)
        self.assertIn("Tool received:", response["response"])
        
        # Verify the last message on the context is the ToolMessage (terminating_config stops after tool call)
        updated_context = Context.get_context(context.context_id)
        # Print all messages for debugging
        for i, msg in enumerate(updated_context.messages):
            print(f"Message {i}: type={msg.get('type')}, content={msg.get('content', '')[:100] if msg.get('content') else 'N/A'}...")
        
        last_message = updated_context.messages[-1]
        self.assertEqual(last_message.get("type"), "tool")
        self.assertIn("Tool received:", last_message.get("content", ""))
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(tool.tool_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_terminating_config_with_nudge(self):
        """Test terminating_config triggers nudge when agent returns content instead of calling terminating tool"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        
        # Create parameter definition for the tool
        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "result",
                    "description": "The final result of the completed task",
                    "type": "string",
                    "parameters": []
                }
            ]
        )
        
        # Create a terminating tool that returns a specific message
        tool_code = '''
def complete_task(result):
    return f"Task completed with result: {result}"
'''
        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="complete_task",
            description="Call this tool when you have completed your task and have a final result to return",
            code=tool_code,
            pd_id=pd.pd_id,
            pass_context=False,
            is_async=False
        )
        
        # Create an agent with the tool
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-terminating",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="You are an assistant. You have a complete_task tool. When asked to complete a task, call the complete_task tool with the result.",
            tools=[tool.tool_id]
        )
        
        # Create a normal context
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )
        
        # Call chat endpoint with terminating_config, using a vague message that might cause 
        # the agent to respond with content first (triggering nudge)
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hi there!",
                "terminating_config": {
                    "tool_ids": [tool.tool_id],
                    "consecutive_nudges": 2,
                    "nudge_message": "You are currently in an autonomous execution mode with no user interaction. You must complete your task by calling the complete_task tool.",
                    "max_invocations": 10
                }
            },
            headers={
                "Authorization": access_token
            }
        )
        
        result = lambda_handler(request, None)
        
        # Check the response
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        print("Terminating config response:", json.dumps(response, indent=2))
        
        # Verify the response is from the terminating tool
        self.assertIn("response", response)
        self.assertIn("Task completed with result:", response["response"])
        
        # Verify the context has the nudge system message (agent likely responded with content first)
        updated_context = Context.get_context(context.context_id)
        
        # Look for the nudge message in the context
        nudge_found = False
        for msg in updated_context.messages:
            if msg.get("type") == "system" and "autonomous execution mode" in msg.get("content", ""):
                nudge_found = True
                break
        
        print(f"Nudge message found: {nudge_found}")
        print(f"Total messages in context: {len(updated_context.messages)}")
        
        # Print all messages for debugging
        for i, msg in enumerate(updated_context.messages):
            print(f"Message {i}: type={msg.get('type')}, content={msg.get('content', '')[:100] if msg.get('content') else 'N/A'}...")
        
        # Verify the last message is the tool response
        last_message = updated_context.messages[-1]
        self.assertEqual(last_message.get("type"), "tool")
        self.assertIn("Task completed with result:", last_message.get("content", ""))
        
        # Test 3: Call invoke again WITHOUT terminating_config and verify we get a normal response
        invoke_request = create_request(
            method="POST",
            path="/chat/invoke",
            body={
                "context_id": context.context_id,
                "save_ai_messages": True
            },
            headers={
                "Authorization": access_token
            }
        )
        
        invoke_result = lambda_handler(invoke_request, None)
        
        # Check the invoke response
        self.assertEqual(invoke_result["statusCode"], 200)
        invoke_response = json.loads(invoke_result["body"])
        print("Invoke response (no terminating config):", json.dumps(invoke_response, indent=2))
        
        # Verify we got a normal content response (not a tool call response)
        self.assertIn("response", invoke_response)
        self.assertIsNotNone(invoke_response["response"])
        self.assertGreater(len(invoke_response["response"]), 0)
        
        # The response should NOT be from the terminating tool since we didn't use terminating_config
        # (agent should respond normally to continue the conversation)
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(tool.tool_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)
        
        