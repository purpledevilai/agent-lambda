import sys
sys.path.append("../")

import unittest
import json
from src.lambda_function import lambda_handler
from tests.config import access_token
from tests.helper_funcs import create_request
from Models import Agent, Tool, Context, User, ParameterDefinition
from AWS import Cognito


class TestAsyncTools(unittest.TestCase):
    
    def test_create_async_tool(self):
        """Test creating a tool with is_async flag set to True"""
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        
        # Create an async tool
        async_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="get_approval",
            description="Get approval from admin",
            code="def get_approval(quote_amount, tool_call_id, context):\n    # Send notification to admin\n    return 'Notification sent'",
            pass_context=True,
            is_async=True
        )
        
        # Verify the tool was created with is_async=True
        self.assertTrue(async_tool.is_async)
        self.assertTrue(async_tool.pass_context)
        
        # Retrieve the tool and verify
        retrieved_tool = Tool.get_tool(async_tool.tool_id)
        self.assertTrue(retrieved_tool.is_async)
        
        # Clean up
        Tool.delete_tool(async_tool.tool_id)
    
    def test_agent_with_async_tool_immediate_response(self):
        """Test that async tools create immediate ToolMessages with their quick response"""
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        
        # Create parameter definition for the tool
        parameter_definition = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "message",
                    "description": "The message to send in the notification",
                    "type": "string"
                }
            ]
        )
        
        # Create an async tool that returns an immediate acknowledgment
        async_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="send_notification",
            description="Send a notification (async)",
            pd_id=parameter_definition.pd_id,
            code="def send_notification(message, tool_call_id):\n    return 'Notification queued for delivery'",
            is_async=True
        )
        
        # Create an agent with this async tool
        agent = Agent.create_agent(
            agent_name="async-agent",
            agent_description="Agent with async tool",
            prompt="You are a helpful assistant. Use the send_notification tool when asked to send notifications.",
            org_id=user.organizations[0],
            is_public=False,
            tools=[async_tool.tool_id]
        )
        
        # Create a context
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )
        
        # Send a message asking to use the async tool
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Please send a notification saying 'Hello World'",
                "save_ai_messages": True
            },
            headers={"Authorization": access_token}
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        response = json.loads(result["body"])
        
        # Check generated messages - should have both tool call and immediate tool response
        generated_messages = response["generated_messages"]
        
        # Should have at least one tool call message
        tool_call_messages = [msg for msg in generated_messages if msg.get("type") == "tool_call"]
        self.assertGreater(len(tool_call_messages), 0)
        
        # Check if the tool call is for send_notification
        has_send_notification = any(
            msg.get("tool_name") == "send_notification" 
            for msg in tool_call_messages
        )
        self.assertTrue(has_send_notification, "Agent should have called the async tool")
        
        # Get the tool_call_id for send_notification
        send_notification_call_id = next(
            msg["tool_call_id"] for msg in tool_call_messages 
            if msg.get("tool_name") == "send_notification"
        )
        
        # Should HAVE an immediate tool response for this async tool
        tool_response_messages = [
            msg for msg in generated_messages 
            if msg.get("type") == "tool_response" and msg.get("tool_call_id") == send_notification_call_id
        ]
        self.assertEqual(len(tool_response_messages), 1, "Async tools should create immediate tool responses")
        
        # Verify the immediate response content
        immediate_response = tool_response_messages[0]["tool_output"]
        self.assertIn("queued", immediate_response.lower(), "Immediate response should indicate the action was queued/started")
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(async_tool.tool_id)
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)
    
    def test_on_tool_call_response_endpoint(self):
        """Test the /on-tool-call-response endpoint"""
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        
        # Create an async tool
        async_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="request_approval",
            description="Request approval for an action (async)",
            code="def request_approval(action, tool_call_id):\n    return 'Approval request sent'",
            is_async=True
        )
        
        # Create an agent with a prompt that encourages using the async tool
        agent = Agent.create_agent(
            agent_name="test-async-agent",
            agent_description="Test agent",
            prompt="You are a helpful assistant. When asked to request approval, use the request_approval tool.",
            org_id=user.organizations[0],
            is_public=False,
            tools=[async_tool.tool_id]
        )
        
        # Create a context
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )
        
        # Invoke the agent to call the async tool
        chat_request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Please request approval for 'deploy to production'",
                "save_ai_messages": True
            },
            headers={"Authorization": access_token}
        )
        
        chat_result = lambda_handler(chat_request, None)
        self.assertEqual(chat_result["statusCode"], 200)
        
        # Load the context and find the tool_call_id
        context = Context.get_context(context.context_id)
        tool_call_id = None
        
        # Search through messages to find the async tool call
        for message in context.messages:
            if message.get("type") == "ai" and message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    if tool_call.get("name") == "request_approval":
                        tool_call_id = tool_call.get("id")
                        break
            if tool_call_id:
                break
        
        # Verify we found a tool call
        self.assertIsNotNone(tool_call_id, "Agent should have called the async tool")
        
        # Now send a response via the /on-tool-call-response endpoint
        request = create_request(
            method="POST",
            path="/on-tool-call-response",
            body={
                "context_id": context.context_id,
                "tool_call_id": tool_call_id,
                "response": "APPROVED: Manager approved the deployment"
            },
            headers={"Authorization": access_token}
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        response = json.loads(result["body"])
        self.assertTrue(response["success"])
        
        # Verify the response was added to the async_tool_response_queue
        updated_context = Context.get_context(context.context_id)
        self.assertEqual(len(updated_context.async_tool_response_queue), 1)
        self.assertEqual(updated_context.async_tool_response_queue[0]["tool_call_id"], tool_call_id)
        self.assertEqual(updated_context.async_tool_response_queue[0]["response"], "APPROVED: Manager approved the deployment")
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(async_tool.tool_id)
    
    def test_end_to_end_approval_workflow(self):
        """
        Comprehensive end-to-end test for async approval workflow.
        Tests the complete flow: request approval -> continue conversation -> receive approval -> agent acknowledges
        """
        print("\n=== Starting End-to-End Approval Workflow Test ===\n")
        
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        
        # Step 1: Create an async approval tool
        print("Step 1: Creating async approval tool...")
        async_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="request_approval",
            description="Request approval from a manager for large purchases over $1000. Use this tool when a customer wants to make a purchase that requires approval.",
            code="def request_approval(purchase_amount, customer_name, tool_call_id):\n    return 'Approval request sent to manager'",
            is_async=True
        )
        print(f"  ✓ Created async tool: {async_tool.name} (ID: {async_tool.tool_id})")
        
        # Step 2: Create an agent with the async tool
        print("\nStep 2: Creating sales agent...")
        agent = Agent.create_agent(
            agent_name="sales-agent-async",
            agent_description="Sales agent that requires approval for large purchases",
            prompt="""You are a helpful sales assistant. 

IMPORTANT RULES:
- For purchases over $1000, you MUST use the request_approval tool first
- After requesting approval, inform the customer that you're waiting for manager approval
- You can continue answering other questions while waiting for approval
- When you receive an approval response, acknowledge it and proceed with the sale""",
            org_id=user.organizations[0],
            is_public=False,
            tools=[async_tool.tool_id]
        )
        print(f"  ✓ Created agent: {agent.agent_name} (ID: {agent.agent_id})")
        
        # Step 3: Create a context
        print("\nStep 3: Creating conversation context...")
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )
        print(f"  ✓ Created context (ID: {context.context_id})")
        
        # Step 4: Customer requests a large purchase (triggers async tool)
        print("\nStep 4: Customer requests large purchase (should trigger approval request)...")
        chat_request_1 = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "I'd like to purchase 50 units at $100 each, total $5000",
                "save_ai_messages": True
            },
            headers={"Authorization": access_token}
        )
        
        result_1 = lambda_handler(chat_request_1, None)
        self.assertEqual(result_1["statusCode"], 200)
        response_1 = json.loads(result_1["body"])
        
        print(f"  Agent response: {response_1['response']}")
        print(f"  Generated messages: {len(response_1['generated_messages'])} messages")
        
        # Step 5: Extract the tool_call_id from the context
        print("\nStep 5: Extracting tool_call_id from async tool call...")
        context = Context.get_context(context.context_id)
        tool_call_id = None
        
        for message in context.messages:
            if message.get("type") == "ai" and message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    if tool_call.get("name") == "request_approval":
                        tool_call_id = tool_call.get("id")
                        print(f"  ✓ Found async tool call (ID: {tool_call_id})")
                        print(f"    Args: {tool_call.get('args')}")
                        break
            if tool_call_id:
                break
        
        self.assertIsNotNone(tool_call_id, "Agent should have called the request_approval tool")
        
        # Step 6: Continue conversation while approval is pending
        print("\nStep 6: Customer asks another question while waiting for approval...")
        chat_request_2 = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "What's your return policy?",
                "save_ai_messages": True
            },
            headers={"Authorization": access_token}
        )
        
        result_2 = lambda_handler(chat_request_2, None)
        self.assertEqual(result_2["statusCode"], 200)
        response_2 = json.loads(result_2["body"])
        
        print(f"  Agent response: {response_2['response']}")
        
        # Verify the queue is still empty (no approval yet)
        context = Context.get_context(context.context_id)
        self.assertEqual(len(context.async_tool_response_queue), 0, "Queue should be empty - approval hasn't arrived yet")
        print("  ✓ Confirmed: No approval response in queue yet")
        
        # Step 7: Manager approves the purchase (via /on-tool-call-response)
        print("\nStep 7: Manager approves the purchase...")
        approval_request = create_request(
            method="POST",
            path="/on-tool-call-response",
            body={
                "context_id": context.context_id,
                "tool_call_id": tool_call_id,
                "response": "APPROVED: Manager John Smith approved the $5000 purchase for 50 units."
            },
            headers={"Authorization": access_token}
        )
        
        approval_result = lambda_handler(approval_request, None)
        self.assertEqual(approval_result["statusCode"], 200)
        approval_response = json.loads(approval_result["body"])
        self.assertTrue(approval_response["success"])
        print("  ✓ Approval response sent to queue")
        
        # Verify the approval is in the queue
        context = Context.get_context(context.context_id)
        self.assertEqual(len(context.async_tool_response_queue), 1)
        print(f"  ✓ Queue now has {len(context.async_tool_response_queue)} response(s)")
        
        # Step 8: Invoke the agent to process the approval
        print("\nStep 8: Invoking agent to process approval response...")
        invoke_request = create_request(
            method="POST",
            path="/chat/invoke",
            body={
                "context_id": context.context_id,
                "save_ai_messages": True
            },
            headers={"Authorization": access_token}
        )
        
        invoke_result = lambda_handler(invoke_request, None)
        self.assertEqual(invoke_result["statusCode"], 200)
        invoke_response = json.loads(invoke_result["body"])
        
        print(f"  Agent response after approval: {invoke_response['response']}")
        print(f"  Generated messages: {len(invoke_response['generated_messages'])} messages")
        
        # Step 9: Verify the approval was processed
        print("\nStep 9: Verifying approval was processed correctly...")
        context = Context.get_context(context.context_id)
        
        # Queue should be empty now
        self.assertEqual(len(context.async_tool_response_queue), 0, "Queue should be empty after processing")
        print("  ✓ Queue cleared after processing")
        
        # Find the tool response message in the context
        tool_response_found = False
        for message in context.messages:
            if message.get("type") == "tool" and message.get("tool_call_id") == tool_call_id:
                tool_response_found = True
                print(f"  ✓ Tool response message added to context")
                print(f"    Content: {message.get('content')[:80]}...")
                break
        
        self.assertTrue(tool_response_found, "Tool response should be in the message history")
        
        # Step 10: Verify agent acknowledged the approval in its response
        print("\nStep 10: Verifying agent acknowledged approval...")
        # The agent should mention approval or acknowledge it in some way
        # (This is somewhat dependent on the LLM's response, but we can check it generated something)
        self.assertIsNotNone(invoke_response['response'])
        self.assertGreater(len(invoke_response['response']), 0)
        print(f"  ✓ Agent generated response: '{invoke_response['response'][:100]}...'")
        
        print("\n=== End-to-End Test Completed Successfully ===\n")
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(async_tool.tool_id)


