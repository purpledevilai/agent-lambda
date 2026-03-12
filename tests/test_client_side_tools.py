import sys
sys.path.append("../")

import unittest
import json
import asyncio
from src.lambda_function import lambda_handler
from tests.config import access_token
from tests.helper_funcs import create_request
from Models import Agent, Tool, Context, User, ParameterDefinition
from AWS import Cognito


class TestClientSideTools(unittest.TestCase):

    def test_create_client_side_tool(self):
        """Test creating a tool with is_client_side_tool flag set to True"""
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        client_side_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="show_confirmation_dialog",
            description="Show a confirmation dialog to the user",
            is_client_side_tool=True
        )

        self.assertTrue(client_side_tool.is_client_side_tool)
        self.assertIsNone(client_side_tool.code)

        retrieved_tool = Tool.get_tool(client_side_tool.tool_id)
        self.assertTrue(retrieved_tool.is_client_side_tool)
        self.assertIsNone(retrieved_tool.code)

        Tool.delete_tool(client_side_tool.tool_id)

    def test_chat_returns_client_side_tool_calls(self):
        """Test that chat response includes client_side_tool_calls when the agent calls a client-side tool"""
        print("\n=== test_chat_returns_client_side_tool_calls ===\n")

        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "message",
                    "description": "The confirmation message to display",
                    "type": "string"
                }
            ]
        )

        client_side_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="show_confirmation",
            description="Show a confirmation dialog to the user in their browser. Use this when you need the user to confirm an action.",
            pd_id=pd.pd_id,
            is_client_side_tool=True
        )

        agent = Agent.create_agent(
            agent_name="client-side-tool-agent",
            agent_description="Agent with client-side tool",
            prompt="You are a helpful assistant. When the user asks you to confirm something, use the show_confirmation tool. Always call the tool, do not just respond with text.",
            org_id=user.organizations[0],
            is_public=False,
            tools=[client_side_tool.tool_id]
        )

        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Please confirm that I want to delete my account",
                "save_ai_messages": True
            },
            headers={"Authorization": access_token}
        )

        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)

        response = json.loads(result["body"])
        print(f"  Response: {response['response']}")
        print(f"  Client side tool calls: {response.get('client_side_tool_calls')}")

        self.assertIsNotNone(response.get("client_side_tool_calls"), "Response should include client_side_tool_calls")
        self.assertGreater(len(response["client_side_tool_calls"]), 0)

        tool_call = response["client_side_tool_calls"][0]
        self.assertEqual(tool_call["tool_name"], "show_confirmation")
        self.assertIn("tool_call_id", tool_call)
        self.assertIn("tool_input", tool_call)

        # Verify no ToolMessage was added for the client-side tool
        updated_context = Context.get_context(context.context_id)
        tool_messages = [
            msg for msg in updated_context.messages
            if msg.get("type") == "tool" and msg.get("tool_call_id") == tool_call["tool_call_id"]
        ]
        self.assertEqual(len(tool_messages), 0, "No ToolMessage should exist for client-side tool yet")

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(client_side_tool.tool_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_client_side_tool_responses_endpoint(self):
        """Full flow: chat triggers client-side tool, then call /chat/client-side-tool-responses with the result"""
        print("\n=== test_client_side_tool_responses_endpoint ===\n")

        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "question",
                    "description": "The yes/no question to ask the user",
                    "type": "string"
                }
            ]
        )

        client_side_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="ask_user_confirmation",
            description="Ask the user a yes/no question and wait for their response. Use this when you need the user to confirm something.",
            pd_id=pd.pd_id,
            is_client_side_tool=True
        )

        agent = Agent.create_agent(
            agent_name="cst-response-agent",
            agent_description="Agent for client-side tool response test",
            prompt="You are a helpful assistant. When the user asks to delete something, use the ask_user_confirmation tool to confirm first. After receiving confirmation, acknowledge the result.",
            org_id=user.organizations[0],
            is_public=False,
            tools=[client_side_tool.tool_id]
        )

        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Step 1: Chat triggers client-side tool
        print("Step 1: Sending chat message to trigger client-side tool...")
        chat_request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Delete my account please",
                "save_ai_messages": True
            },
            headers={"Authorization": access_token}
        )

        chat_result = lambda_handler(chat_request, None)
        self.assertEqual(chat_result["statusCode"], 200)

        chat_response = json.loads(chat_result["body"])
        self.assertIsNotNone(chat_response.get("client_side_tool_calls"))
        self.assertGreater(len(chat_response["client_side_tool_calls"]), 0)

        tool_call = chat_response["client_side_tool_calls"][0]
        tool_call_id = tool_call["tool_call_id"]
        print(f"  Client-side tool call: {tool_call['tool_name']} (ID: {tool_call_id})")

        # Step 2: Send client-side tool response
        print("Step 2: Sending client-side tool response...")
        response_request = create_request(
            method="POST",
            path="/chat/client-side-tool-responses",
            body={
                "context_id": context.context_id,
                "tool_responses": [
                    {
                        "tool_call_id": tool_call_id,
                        "response": "Yes, confirmed. Delete the account."
                    }
                ]
            },
            headers={"Authorization": access_token}
        )

        response_result = lambda_handler(response_request, None)
        self.assertEqual(response_result["statusCode"], 200)

        response_body = json.loads(response_result["body"])
        print(f"  Agent response after tool response: {response_body['response']}")

        self.assertIsNotNone(response_body["response"])
        self.assertGreater(len(response_body["response"]), 0)
        self.assertTrue(response_body["saved_ai_messages"])

        # Verify context was updated with the tool response
        updated_context = Context.get_context(context.context_id)
        tool_messages = [
            msg for msg in updated_context.messages
            if msg.get("type") == "tool" and msg.get("tool_call_id") == tool_call_id
        ]
        self.assertEqual(len(tool_messages), 1, "ToolMessage should exist for the client-side tool response")

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(client_side_tool.tool_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_mixed_server_and_client_side_tools(self):
        """Test agent with both server-side and client-side tools called in the same turn"""
        print("\n=== test_mixed_server_and_client_side_tools ===\n")

        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create parameter definitions
        server_pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "query",
                    "description": "The search query",
                    "type": "string"
                }
            ]
        )

        client_pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "items",
                    "description": "Comma-separated list of items to display",
                    "type": "string"
                }
            ]
        )

        # Server-side tool
        server_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="search_database",
            description="Search the database for items matching a query",
            pd_id=server_pd.pd_id,
            code="def search_database(query):\n    return 'Found items: laptop, phone, tablet'",
        )

        # Client-side tool
        client_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="display_results_ui",
            description="Display search results in a rich UI on the client. Always call this after getting search results to show them nicely to the user.",
            pd_id=client_pd.pd_id,
            is_client_side_tool=True
        )

        agent = Agent.create_agent(
            agent_name="mixed-tools-agent",
            agent_description="Agent with both server and client-side tools",
            prompt="You are a shopping assistant. When a user searches for something, first use search_database to find items, then use display_results_ui to show them. Always call both tools.",
            org_id=user.organizations[0],
            is_public=False,
            tools=[server_tool.tool_id, client_tool.tool_id]
        )

        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Step 1: Chat triggers both tools
        print("Step 1: Sending search query...")
        chat_request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Search for electronics",
                "save_ai_messages": True
            },
            headers={"Authorization": access_token}
        )

        chat_result = lambda_handler(chat_request, None)
        self.assertEqual(chat_result["statusCode"], 200)

        chat_response = json.loads(chat_result["body"])
        print(f"  Response: {chat_response['response']}")
        print(f"  Generated messages: {len(chat_response['generated_messages'])}")
        print(f"  Client side tool calls: {chat_response.get('client_side_tool_calls')}")

        # Verify server tool executed (ToolMessage exists)
        updated_context = Context.get_context(context.context_id)
        search_tool_responses = [
            msg for msg in updated_context.messages
            if msg.get("type") == "tool" and "Found items" in (msg.get("content") or "")
        ]
        print(f"  Server-side tool responses found: {len(search_tool_responses)}")
        self.assertGreater(len(search_tool_responses), 0, "Server-side tool should have executed")

        # Check if client-side tool calls were returned
        if chat_response.get("client_side_tool_calls"):
            print("  Client-side tool calls detected, sending response...")
            tool_call = chat_response["client_side_tool_calls"][0]

            # Step 2: Send client-side tool response
            response_request = create_request(
                method="POST",
                path="/chat/client-side-tool-responses",
                body={
                    "context_id": context.context_id,
                    "tool_responses": [
                        {
                            "tool_call_id": tool_call["tool_call_id"],
                            "response": "Results displayed successfully"
                        }
                    ]
                },
                headers={"Authorization": access_token}
            )

            response_result = lambda_handler(response_request, None)
            self.assertEqual(response_result["statusCode"], 200)
            response_body = json.loads(response_result["body"])
            print(f"  Agent response after client tool: {response_body['response']}")
        else:
            print("  No client-side tool calls in this turn (agent may have called them sequentially)")

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(server_tool.tool_id)
        Tool.delete_tool(client_tool.tool_id)
        ParameterDefinition.delete_parameter_definition(server_pd.pd_id)
        ParameterDefinition.delete_parameter_definition(client_pd.pd_id)

    def test_client_side_tool_responses_missing_response_error(self):
        """Test that endpoint errors when not all client-side tool responses are provided"""
        print("\n=== test_client_side_tool_responses_missing_response_error ===\n")

        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "message",
                    "description": "The notification message",
                    "type": "string"
                }
            ]
        )

        client_side_tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="show_notification",
            description="Show a notification to the user. Always use this tool when the user asks you to notify them.",
            pd_id=pd.pd_id,
            is_client_side_tool=True
        )

        agent = Agent.create_agent(
            agent_name="cst-error-agent",
            agent_description="Agent for error test",
            prompt="You are a helpful assistant. When the user asks for a notification, use the show_notification tool.",
            org_id=user.organizations[0],
            is_public=False,
            tools=[client_side_tool.tool_id]
        )

        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Trigger client-side tool
        chat_request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Notify me that the build succeeded",
                "save_ai_messages": True
            },
            headers={"Authorization": access_token}
        )

        chat_result = lambda_handler(chat_request, None)
        self.assertEqual(chat_result["statusCode"], 200)
        chat_response = json.loads(chat_result["body"])
        self.assertIsNotNone(chat_response.get("client_side_tool_calls"))

        # Send empty tool_responses (missing the required ones)
        response_request = create_request(
            method="POST",
            path="/chat/client-side-tool-responses",
            body={
                "context_id": context.context_id,
                "tool_responses": []
            },
            headers={"Authorization": access_token}
        )

        response_result = lambda_handler(response_request, None)
        self.assertIn(response_result["statusCode"], [400, 500])
        print(f"  Error response (expected): {response_result['body']}")

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(client_side_tool.tool_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_token_streaming_client_side_tools(self):
        """Test TokenStreamingAgentChat handles client-side tools correctly"""
        print("\n=== test_token_streaming_client_side_tools ===\n")

        from LLM.TokenStreamingAgentChat import TokenStreamingAgentChat
        from LLM.AgentTool import AgentTool
        from LLM.CreateLLM import create_llm
        from pydantic import BaseModel, Field

        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create a client-side tool as AgentTool directly
        class show_dialog(BaseModel):
            """Show a dialog to the user"""
            message: str = Field(description="The dialog message")

        client_tool = AgentTool(
            tool_id="test-client-side-tool",
            function=lambda **kwargs: "",
            params=show_dialog,
            is_client_side_tool=True
        )

        # Create an agent and context for the LLM
        agent = Agent.create_agent(
            agent_name="streaming-cst-agent",
            agent_description="Agent for streaming client-side tool test",
            prompt="You are a helpful assistant. When the user asks you to show something, use the show_dialog tool. Always call the tool.",
            org_id=user.organizations[0],
            is_public=False,
        )

        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        llm = create_llm(None, for_streaming=True)

        agent_chat = TokenStreamingAgentChat(
            llm=llm,
            prompt=agent.prompt,
            tools=[client_tool],
            messages=[],
            context=context.model_dump(),
        )

        # Run the invoke asynchronously
        async def run_test():
            from langchain_core.messages import HumanMessage
            agent_chat.messages.append(HumanMessage(content="Show me a welcome dialog"))
            token_stream = await agent_chat.invoke()

            tokens = []
            if token_stream:
                async for token in token_stream:
                    tokens.append(token)

            return tokens

        tokens = asyncio.get_event_loop().run_until_complete(run_test())
        print(f"  Tokens received: {len(tokens)}")
        print(f"  Pending client-side tool calls: {agent_chat.pending_client_side_tool_calls}")

        # Verify pending_client_side_tool_calls is set
        self.assertIsNotNone(agent_chat.pending_client_side_tool_calls)
        self.assertGreater(len(agent_chat.pending_client_side_tool_calls), 0)

        tool_call = agent_chat.pending_client_side_tool_calls[0]
        self.assertEqual(tool_call["tool_name"], "show_dialog")
        self.assertIn("tool_call_id", tool_call)
        self.assertIn("tool_input", tool_call)

        # Verify name_to_tool_id was built
        self.assertIn("show_dialog", agent_chat.name_to_tool_id)
        self.assertEqual(agent_chat.name_to_tool_id["show_dialog"], "test-client-side-tool")

        # Now simulate the client-side tool response and continue
        from langchain_core.messages import ToolMessage
        agent_chat.messages.append(
            ToolMessage(
                tool_call_id=tool_call["tool_call_id"],
                content="Dialog shown successfully"
            )
        )
        agent_chat.pending_client_side_tool_calls = None

        async def run_continuation():
            token_stream = await agent_chat.invoke()
            tokens = []
            if token_stream:
                async for token in token_stream:
                    tokens.append(token)
            return tokens

        continuation_tokens = asyncio.get_event_loop().run_until_complete(run_continuation())
        print(f"  Continuation tokens: {len(continuation_tokens)}")
        print(f"  Total messages: {len(agent_chat.messages)}")

        # After continuation there should be AI content (agent acknowledging the tool response)
        self.assertGreater(len(continuation_tokens), 0, "Agent should respond after receiving tool response")

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
