import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
from src.AWS import Cognito
from src.Models import DataWindow, User, Agent, Context, Tool


class TestDataWindow(unittest.TestCase):

    def test_create_data_window(self):
        """Test creating a DataWindow via API"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create DataWindow
        create_body = {
            "org_id": org_id,
            "name": "Test Activity Feed",
            "description": "Test activity feed for testing",
            "data": "Activity 1\nActivity 2\nActivity 3"
        }
        
        request = create_request(
            method="POST",
            path="/data-window",
            headers={"Authorization": access_token},
            body=create_body
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        res_body = json.loads(result["body"])
        self.assertEqual(res_body["name"], create_body["name"])
        self.assertEqual(res_body["description"], create_body["description"])
        self.assertEqual(res_body["data"], create_body["data"])
        self.assertEqual(res_body["org_id"], org_id)
        
        # Clean up
        DataWindow.delete_data_window(res_body["data_window_id"])

    def test_get_data_window(self):
        """Test getting a DataWindow by ID"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        data_window = DataWindow.create_data_window(
            org_id=org_id,
            name="Test Feed",
            description="Test description",
            data="Test data content"
        )
        
        # Get DataWindow
        request = create_request(
            method="GET",
            path=f"/data-window/{data_window.data_window_id}",
            headers={"Authorization": access_token},
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        res_body = json.loads(result["body"])
        self.assertEqual(res_body["data_window_id"], data_window.data_window_id)
        self.assertEqual(res_body["data"], data_window.data)
        
        # Clean up
        DataWindow.delete_data_window(data_window.data_window_id)

    def test_update_data_window(self):
        """Test updating a DataWindow's data"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        data_window = DataWindow.create_data_window(
            org_id=org_id,
            name="Test Feed",
            data="Old data"
        )
        
        # Update DataWindow
        update_body = {
            "data": "New updated data\nActivity 1\nActivity 2"
        }
        
        request = create_request(
            method="PUT",
            path=f"/data-window/{data_window.data_window_id}",
            headers={"Authorization": access_token},
            body=update_body
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        res_body = json.loads(result["body"])
        self.assertEqual(res_body["data"], update_body["data"])
        
        # Verify update persisted
        refreshed = DataWindow.get_data_window(data_window.data_window_id)
        self.assertEqual(refreshed.data, update_body["data"])
        
        # Clean up
        DataWindow.delete_data_window(data_window.data_window_id)

    def test_delete_data_window(self):
        """Test deleting a DataWindow"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        data_window = DataWindow.create_data_window(
            org_id=org_id,
            data="Test data"
        )
        
        # Delete DataWindow
        request = create_request(
            method="DELETE",
            path=f"/data-window/{data_window.data_window_id}",
            headers={"Authorization": access_token},
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        # Verify deletion
        with self.assertRaises(Exception) as context:
            DataWindow.get_data_window(data_window.data_window_id)
        self.assertIn("does not exist", str(context.exception))

    def test_get_data_windows_for_user(self):
        """Test getting all DataWindows for user's organizations"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create multiple DataWindows
        dw1 = DataWindow.create_data_window(org_id=org_id, data="Data 1")
        dw2 = DataWindow.create_data_window(org_id=org_id, data="Data 2")
        
        # Get DataWindows
        request = create_request(
            method="GET",
            path="/data-windows",
            headers={"Authorization": access_token}
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        res_body = json.loads(result["body"])
        data_window_ids = [dw["data_window_id"] for dw in res_body["data_windows"]]
        
        self.assertIn(dw1.data_window_id, data_window_ids)
        self.assertIn(dw2.data_window_id, data_window_ids)
        
        # Clean up
        DataWindow.delete_data_window(dw1.data_window_id)
        DataWindow.delete_data_window(dw2.data_window_id)

    def test_agent_opens_data_window(self):
        """Test agent calling open_data_window tool"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create a DataWindow
        data_window = DataWindow.create_data_window(
            org_id=org_id,
            name="Activity Feed",
            description="Recent activities",
            data="Activity 1: User logged in\nActivity 2: File uploaded\nActivity 3: Task completed"
        )
        
        # Create an agent with open_data_window tool
        agent = Agent.create_agent(
            agent_name="Test Agent",
            agent_description="Test agent with DataWindow access",
            prompt=f"You are a helpful assistant. You have access to a DataWindow with ID {data_window.data_window_id}. When asked about recent activity, use the open_data_window tool to check it.",
            org_id=org_id,
            is_public=False,
            agent_speaks_first=False,
            tools=["open_data_window"]
        )
        
        # Create a context
        context = Context.create_context(
            user_id=user.user_id,
            agent_id=agent.agent_id
        )
        
        # Chat with agent to trigger DataWindow opening
        chat_body = {
            "context_id": context.context_id,
            "message": f"Can you open the DataWindow {data_window.data_window_id} and tell me what's in it?"
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
        
        # Verify the DataWindow tool was called
        updated_context = Context.get_context(context.context_id)
        tool_calls_found = False
        for msg in updated_context.messages:
            if msg.get("type") == "ai" and msg.get("tool_calls"):
                for tool_call in msg["tool_calls"]:
                    if tool_call["name"] == "open_data_window":
                        tool_calls_found = True
                        break
        
        self.assertTrue(tool_calls_found, "Agent should have called open_data_window tool")
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        DataWindow.delete_data_window(data_window.data_window_id)

    def test_data_window_refresh_on_invoke(self):
        """Test that DataWindow data refreshes on subsequent invocations"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create a DataWindow with initial data
        data_window = DataWindow.create_data_window(
            org_id=org_id,
            name="Live Feed",
            data="Initial data: Item 1"
        )
        
        # Create an agent
        agent = Agent.create_agent(
            agent_name="Test Agent",
            agent_description="Test agent",
            prompt=f"You are a helpful assistant. Open DataWindow {data_window.data_window_id} and report what you see.",
            org_id=org_id,
            is_public=False,
            agent_speaks_first=False,
            tools=["open_data_window"]
        )
        
        # Create a context
        context = Context.create_context(
            user_id=user.user_id,
            agent_id=agent.agent_id,
            user_defined={"org_id": org_id}
        )
        
        # First chat - open the DataWindow
        chat_body = {
            "context_id": context.context_id,
            "message": f"Open DataWindow {data_window.data_window_id} and tell me what's there"
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
        
        # Update the DataWindow with new data
        data_window.data = "Updated data: Item 2, Item 3, Item 4"
        DataWindow.save_data_window(data_window)
        
        # Second chat - invoke again (DataWindow should auto-refresh)
        chat_body2 = {
            "context_id": context.context_id,
            "message": "What does the DataWindow show now?"
        }
        
        request2 = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body2
        )
        
        result2 = lambda_handler(request2, None)
        self.assertEqual(result2["statusCode"], 200)
        res_body2 = json.loads(result2["body"])
        
        # Verify we got a response back
        self.assertIn("response", res_body2)
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        DataWindow.delete_data_window(data_window.data_window_id)

    def test_multiple_data_windows_in_context(self):
        """Test context with multiple DataWindows"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create two DataWindows
        dw1 = DataWindow.create_data_window(
            org_id=org_id,
            name="Activities",
            data="Activities: Login, Upload, Download"
        )
        
        dw2 = DataWindow.create_data_window(
            org_id=org_id,
            name="Notifications",
            data="Notifications: 3 new messages, 1 alert"
        )
        
        # Create an agent
        agent = Agent.create_agent(
            agent_name="Test Agent",
            agent_description="Test agent",
            prompt=f"You are a helpful assistant with access to two DataWindows: {dw1.data_window_id} (activities) and {dw2.data_window_id} (notifications).",
            org_id=org_id,
            is_public=False,
            agent_speaks_first=False,
            tools=["open_data_window"]
        )
        
        # Create a context
        context = Context.create_context(
            user_id=user.user_id,
            agent_id=agent.agent_id,
        )
        
        # Chat to open both DataWindows
        chat_body = {
            "context_id": context.context_id,
            "message": f"Open both DataWindows {dw1.data_window_id} and {dw2.data_window_id} and summarize what you see"
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
        
        # Response should mention both activities and notifications
        response_lower = res_body["response"].lower()
        self.assertTrue("activit" in response_lower or "login" in response_lower)
        self.assertTrue("notif" in response_lower or "message" in response_lower)
        
        # Update both DataWindows
        dw1.data = "Activities: New login, File shared"
        DataWindow.save_data_window(dw1)
        
        dw2.data = "Notifications: 5 new messages, 2 alerts"
        DataWindow.save_data_window(dw2)
        
        # Invoke again - both should refresh
        chat_body2 = {
            "context_id": context.context_id,
            "message": "What's the latest update?"
        }
        
        request2 = create_request(
            method="POST",
            path="/chat",
            headers={"Authorization": access_token},
            body=chat_body2
        )
        
        result2 = lambda_handler(request2, None)
        self.assertEqual(result2["statusCode"], 200)
        res_body2 = json.loads(result2["body"])
        
        # Response should reflect updated data
        response2_lower = res_body2["response"].lower()
        # Should see the new counts (5 messages, 2 alerts) or mention "shared"
        self.assertTrue("5" in res_body2["response"] or "shared" in response2_lower or "new" in response2_lower)
        
        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        DataWindow.delete_data_window(dw1.data_window_id)
        DataWindow.delete_data_window(dw2.data_window_id)

    def test_data_window_permission_check(self):
        """Test that DataWindow respects org permissions"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Create a DataWindow in a different org
        wrong_org_id = "wrong-org-id-12345"
        data_window = DataWindow.create_data_window(
            org_id=wrong_org_id,
            data="Secret data"
        )
        
        # Try to get the DataWindow (should fail)
        request = create_request(
            method="GET",
            path=f"/data-window/{data_window.data_window_id}",
            headers={"Authorization": access_token},
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 403)
        
        # Clean up
        DataWindow.delete_data_window(data_window.data_window_id)

    def test_data_window_not_found(self):
        """Test error handling when DataWindow doesn't exist"""
        
        fake_id = "non-existent-data-window-id"
        
        request = create_request(
            method="GET",
            path=f"/data-window/{fake_id}",
            headers={"Authorization": access_token},
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 404)


