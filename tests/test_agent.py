import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token, agent_id_outside_of_org
from src.lambda_function import lambda_handler
# Import for test
from src.AWS import Cognito
from src.Models import Agent, User


class TestAgent(unittest.TestCase):

    def test_get_agents(self):

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
        
        # Create request
        request = create_request(
            method="GET",
            path="/agents",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for agents
        self.assertTrue(len(res_body["agents"]) > 0)
        
        # Check if agent id is in agent list
        self.assertTrue(any(agent_data["agent_id"] == agent.agent_id for agent_data in res_body["agents"]), "Agent not found in agent list")

        # Clean up
        Agent.delete_agent(agent.agent_id)

    def test_create_agent(self):
        
        # Create org data
        create_agent_body = {
            "agent_name": "Test Agent",
            "agent_description": "Test Description",
            "prompt": "Test Prompt",
            "is_public": False,
            "agent_speaks_first": False,
        }

        # Create request
        request = create_request(
            method="POST",
            path="/agent",
            headers={
                "Authorization": access_token
            },
            body=create_agent_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_name"], create_agent_body["agent_name"])

        # Clean up
        Agent.delete_agent(res_body["agent_id"])

    def test_get_agent(self):
        
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

        # Create request
        request = create_request(
            method="GET",
            path=f"/agent/{agent.agent_id}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_id"], agent.agent_id)

        # Clean up
        Agent.delete_agent(agent.agent_id)

    def test_get_public_agent(self):

        # Create request
        public_agent_id = "aj-public";
        request = create_request(
            method="GET",
            path=f"/agent/{public_agent_id}"
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_id"], public_agent_id)

    def test_get_agent_outside_org(self):

        # Create request
        request = create_request(
            method="GET",
            path=f"/agent/{agent_id_outside_of_org}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 403)

    def test_update_agent(self):
        
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

        # Create update data
        update_agent_body = {
            "agent_name": "Updated Agent",
            "prompt": "Updated Prompt",
            "agent_speaks_first": True,
        }

        # Create request
        request = create_request(
            method="POST",
            path=f"/agent/{agent.agent_id}",
            headers={
                "Authorization": access_token
            },
            body=update_agent_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_name"], update_agent_body["agent_name"])
        self.assertEqual(res_body["agent_description"], agent.agent_description)
        self.assertEqual(res_body["prompt"], update_agent_body["prompt"])

        # Clean up
        Agent.delete_agent(agent.agent_id)

    def test_delete_agent(self):
        
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

        # Create request
        request = create_request(
            method="DELETE",
            path=f"/agent/{agent.agent_id}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # Check if agent is deleted
        self.assertFalse(Agent.agent_exists(agent.agent_id))

    def test_create_agent_with_tools(self):
        
        # Create org data
        create_agent_body = {
            "agent_name": "Test Agent",
            "agent_description": "Test Description",
            "prompt": "Test Prompt",
            "is_public": False,
            "agent_speaks_first": False,
            "tools": [
                {
                    "name": "pass_event"
                },
            ]
        }

        # Create request
        request = create_request(
            method="POST",
            path="/agent",
            headers={
                "Authorization": access_token
            },
            body=create_agent_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["tools"][0]["name"], create_agent_body["tools"][0]["name"])

        # Clean up
        Agent.delete_agent(res_body["agent_id"])

    def test_create_agent_with_invalid_tool(self):
        
        # Create org data
        create_agent_body = {
            "agent_name": "Test Agent",
            "agent_description": "Test Description",
            "prompt": "Test Prompt",
            "is_public": False,
            "agent_speaks_first": False,
            "tools": [
                {
                    "name": "invalid_tool"
                },
            ]
        }

        # Create request
        request = create_request(
            method="POST",
            path="/agent",
            headers={
                "Authorization": access_token
            },
            body=create_agent_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 400)

    def test_update_agent_tools(self):
        
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
            tools=[
                {
                    "name": "pass_event"
                },
            ]
        )

        # Create update data
        update_agent_body = {
            "tools": [
                {
                    "name": "set-prompt"
                },
            ]
        }

        # Create request
        request = create_request(
            method="POST",
            path=f"/agent/{agent.agent_id}",
            headers={
                "Authorization": access_token
            },
            body=update_agent_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for tools
        self.assertEqual(res_body["tools"][0]["name"], update_agent_body["tools"][0]["name"])

        # Clean up
        Agent.delete_agent(agent.agent_id)

    def test_update_agent_with_invalid_tool(self):
        
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
            tools=[
                {
                    "name": "pass_event"
                },
            ]
        )

        # Create update data
        update_agent_body = {
            "tools": [
                {
                    "name": "invalid_tool"
                },
            ]
        }

        # Create request
        request = create_request(
            method="POST",
            path=f"/agent/{agent.agent_id}",
            headers={
                "Authorization": access_token
            },
            body=update_agent_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 400)

        # Clean up
        Agent.delete_agent(agent.agent_id)

    def test_get_existing_agent_without_uses_prompt_args(self):

        # Create request
        request = create_request(
            method="GET",
            path=f"/agent/aj-public"
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])
        print(res_body)

    def test_create_agent_with_uses_prompt_args(self):
        
        # Create org data
        create_agent_body = {
            "agent_name": "Test Agent",
            "agent_description": "Test Description",
            "prompt": "Test Prompt for {name}",
            "is_public": False,
            "agent_speaks_first": False,
            "uses_prompt_args": True
        }

        # Create request
        request = create_request(
            method="POST",
            path="/agent",
            headers={
                "Authorization": access_token
            },
            body=create_agent_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["uses_prompt_args"], create_agent_body["uses_prompt_args"])

        # Clean up
        Agent.delete_agent(res_body["agent_id"])

    

    