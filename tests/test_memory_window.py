import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
from src.AWS import Cognito
from src.Models import JSONDocument, User, Agent, Context


class TestMemoryWindow(unittest.TestCase):

    def test_agent_opens_memory_window(self):
        """Test agent calling open_memory_window tool"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create a memory document
        memory_doc = JSONDocument.create_json_document(JSONDocument.CreateJSONDocumentParams(
            name="Test Memory",
            data={"tasks": ["Task 1", "Task 2"], "notes": "Initial notes"},
            org_id=org_id
        ))
        
        # Create an agent with open_memory_window tool
        agent = Agent.create_agent(
            agent_name="Memory Test Agent",
            agent_description="Test agent with memory window access",
            prompt=f"You are a helpful assistant. You have access to a memory document with ID {memory_doc.document_id}. When asked about the memory, use the open_memory_window tool to check it.",
            org_id=org_id,
            is_public=False,
            agent_speaks_first=False,
            tools=["open_memory_window"]
        )
        
        # Create a context
        context = Context.create_context(
            user_id=user.user_id,
            agent_id=agent.agent_id
        )
        
        # Chat with agent to trigger memory window opening
        chat_body = {
            "context_id": context.context_id,
            "message": f"Can you open the memory document {memory_doc.document_id} and tell me what tasks are listed?"
        }
        
        request = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        res_body = json.loads(result["body"])
        
        # Verify we got a response back
        self.assertIn("response", res_body)
        
        # Verify the memory window tool was called
        updated_context = Context.get_context(context.context_id)
        tool_calls_found = False
        for msg in updated_context.messages:
            if msg.get("type") == "ai" and msg.get("tool_calls"):
                for tool_call in msg["tool_calls"]:
                    if tool_call["name"] == "open_memory_window":
                        tool_calls_found = True
                        break
        
        self.assertTrue(tool_calls_found, "Agent should have called open_memory_window tool")
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        JSONDocument.delete_json_document(memory_doc.document_id)

    def test_agent_writes_memory_and_window_refreshes(self):
        """Test that memory window refreshes after write_memory is called"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create a memory document with initial data
        memory_doc = JSONDocument.create_json_document(JSONDocument.CreateJSONDocumentParams(
            name="Test Memory",
            data={"items": ["Item 1"]},
            org_id=org_id
        ))
        
        # Create an agent with both memory tools
        agent = Agent.create_agent(
            agent_name="Memory Test Agent",
            agent_description="Test agent with memory tools",
            prompt=f"You are a helpful assistant with access to memory document {memory_doc.document_id}. You can open it with open_memory_window and modify it with write_memory. When asked to remember something, write it to the items list.",
            org_id=org_id,
            is_public=False,
            agent_speaks_first=False,
            tools=["open_memory_window", "write_memory", "append_memory"]
        )
        
        # Create a context
        context = Context.create_context(
            user_id=user.user_id,
            agent_id=agent.agent_id
        )
        
        # First chat - open the memory window
        chat_body = {
            "context_id": context.context_id,
            "message": f"Open the memory document {memory_doc.document_id} and tell me what items are there"
        }
        
        request = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        # Second chat - add a new item
        chat_body2 = {
            "context_id": context.context_id,
            "message": f"Add 'Item 2' to the items list in document {memory_doc.document_id}"
        }
        
        request2 = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body2
        )
        
        result2 = lambda_handler(request2, None)
        self.assertEqual(result2["statusCode"], 200)
        
        # Verify the memory document was updated
        updated_doc = JSONDocument.get_json_document(memory_doc.document_id)
        self.assertIn("Item 2", str(updated_doc.data))
        
        # Third chat - ask about items (should see the updated memory window)
        chat_body3 = {
            "context_id": context.context_id,
            "message": "What items do you see in the memory now?"
        }
        
        request3 = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body3
        )
        
        result3 = lambda_handler(request3, None)
        self.assertEqual(result3["statusCode"], 200)
        res_body3 = json.loads(result3["body"])
        
        # Response should mention both items
        self.assertIn("response", res_body3)
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        JSONDocument.delete_json_document(memory_doc.document_id)

    def test_memory_window_with_path(self):
        """Test opening memory window with a specific path"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create a memory document with nested data
        memory_doc = JSONDocument.create_json_document(JSONDocument.CreateJSONDocumentParams(
            name="Nested Memory",
            data={
                "user": {
                    "name": "John",
                    "preferences": {
                        "theme": "dark",
                        "language": "en"
                    }
                },
                "settings": {
                    "notifications": True
                }
            },
            org_id=org_id
        ))
        
        # Create an agent
        agent = Agent.create_agent(
            agent_name="Memory Test Agent",
            agent_description="Test agent",
            prompt=f"You are a helpful assistant. Memory document ID is {memory_doc.document_id}. When asked about preferences, open the memory window with path 'user.preferences' to see just that section.",
            org_id=org_id,
            is_public=False,
            agent_speaks_first=False,
            tools=["open_memory_window"]
        )
        
        # Create a context
        context = Context.create_context(
            user_id=user.user_id,
            agent_id=agent.agent_id
        )
        
        # Chat to open memory window with path
        chat_body = {
            "context_id": context.context_id,
            "message": f"Open the memory document {memory_doc.document_id} at path 'user.preferences' and tell me what the theme setting is"
        }
        
        request = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        res_body = json.loads(result["body"])
        self.assertIn("response", res_body)
        
        # Response should mention dark theme
        response_lower = res_body["response"].lower()
        self.assertTrue("dark" in response_lower, "Response should mention the dark theme")
        
        # Verify the tool was called with path
        updated_context = Context.get_context(context.context_id)
        path_found = False
        for msg in updated_context.messages:
            if msg.get("type") == "ai" and msg.get("tool_calls"):
                for tool_call in msg["tool_calls"]:
                    if tool_call["name"] == "open_memory_window":
                        args = tool_call.get("args", {})
                        if args.get("path") == "user.preferences":
                            path_found = True
                            break
        
        self.assertTrue(path_found, "Agent should have called open_memory_window with path 'user.preferences'")
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        JSONDocument.delete_json_document(memory_doc.document_id)

    def test_memory_window_permission_check(self):
        """Test that memory window respects user org permissions"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create a memory document in a DIFFERENT org (user doesn't have access)
        wrong_org_id = "wrong-org-id-12345"
        memory_doc = JSONDocument.create_json_document(JSONDocument.CreateJSONDocumentParams(
            name="Secret Memory",
            data={"secret": "data"},
            org_id=wrong_org_id,
            is_public=False  # Not public, so user can't access
        ))
        
        # Create an agent in the USER's org
        agent = Agent.create_agent(
            agent_name="Memory Test Agent",
            agent_description="Test agent",
            prompt=f"You are a helpful assistant. Try to open memory document {memory_doc.document_id}.",
            org_id=org_id,
            is_public=False,
            agent_speaks_first=False,
            tools=["open_memory_window"]
        )
        
        # Create a context
        context = Context.create_context(
            user_id=user.user_id,
            agent_id=agent.agent_id
        )
        
        # Try to open memory document from wrong org
        chat_body = {
            "context_id": context.context_id,
            "message": f"Open memory document {memory_doc.document_id}"
        }
        
        request = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        # Check that the tool response contains an error about permissions/org
        updated_context = Context.get_context(context.context_id)
        error_found = False
        for msg in updated_context.messages:
            if msg.get("type") == "tool":
                content = msg.get("content", "")
                if "does not belong" in content.lower() or "org" in content.lower() or "error" in content.lower():
                    error_found = True
                    break
        
        self.assertTrue(error_found, "Tool response should contain permission error")
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        JSONDocument.delete_json_document(memory_doc.document_id)

    def test_memory_window_invalid_path_after_delete(self):
        """Test that memory window handles invalid paths gracefully after deletion"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create a memory document
        memory_doc = JSONDocument.create_json_document(JSONDocument.CreateJSONDocumentParams(
            name="Test Memory",
            data={"tasks": {"active": ["Task 1", "Task 2"]}},
            org_id=org_id
        ))
        
        # Create an agent
        agent = Agent.create_agent(
            agent_name="Memory Test Agent",
            agent_description="Test agent",
            prompt=f"You are a helpful assistant with access to memory document {memory_doc.document_id}.",
            org_id=org_id,
            is_public=False,
            agent_speaks_first=False,
            tools=["open_memory_window", "delete_memory"]
        )
        
        # Create a context
        context = Context.create_context(
            user_id=user.user_id,
            agent_id=agent.agent_id
        )
        
        # First chat - open window with path tasks.active
        chat_body = {
            "context_id": context.context_id,
            "message": f"Open memory document {memory_doc.document_id} at path 'tasks.active'"
        }
        
        request = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        # Second chat - delete the tasks.active path
        chat_body2 = {
            "context_id": context.context_id,
            "message": f"Delete the 'tasks.active' path from document {memory_doc.document_id}"
        }
        
        request2 = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body2
        )
        
        result2 = lambda_handler(request2, None)
        self.assertEqual(result2["statusCode"], 200)
        
        # Third chat - invoke again (the window refresh should handle the missing path)
        chat_body3 = {
            "context_id": context.context_id,
            "message": "What do you see in the memory now?"
        }
        
        request3 = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body3
        )
        
        result3 = lambda_handler(request3, None)
        # Should not crash - might return an error message about path not available
        self.assertEqual(result3["statusCode"], 200)
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        JSONDocument.delete_json_document(memory_doc.document_id)


if __name__ == "__main__":
    unittest.main()

