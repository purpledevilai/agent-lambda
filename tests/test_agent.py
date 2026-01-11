import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token, agent_id_outside_of_org
from src.lambda_function import lambda_handler
# Import for test
from src.AWS import Cognito
from src.Models import Agent, User, ParameterDefinition, Tool, Context


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
                "pass_event"
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
        self.assertEqual(res_body["tools"][0], "pass_event")

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
                "invalid_tool"
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
        self.assertEqual(result["statusCode"], 404)

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
                "pass_event"
            ]
        )

        # Create update data
        update_agent_body = {
            "tools": [
               "invalid_tool"
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
        self.assertEqual(result["statusCode"], 404)

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

    def test_agent_with_user_defined_tool(self):

        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create parameter definition
        parameter_definition = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "lat",
                    "description": "The latitude of the location",
                    "type": "string"
                },
                {
                    "name": "long",
                    "description": "The longitude of the location",
                    "type": "string"
                }
            ]
        )

        # Create tool
        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="get_weather",
            description="Gets the weather in the specified location",
            pd_id=parameter_definition.pd_id,
            code="def get_weather(lat, long):\n  url = f\"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current=temperature_2m\"\n\n  try:\n    data = requests.get(url).json()\n    return data[\"current\"][\"temperature_2m\"]  # Extract temperature\n  except Exception as e:\n    return f\"Error fetching temperature: {e}\""
        )

        # Create agent
        agent: Agent.Agent = Agent.create_agent(
            agent_name="Weather Agent",
            agent_description="Can get you the weather",
            prompt="When the user asks for the weather, call the get_weather tool with the latitude and longitude, you know that the lat and long for melbourne are -37 and 144",
            org_id=user.organizations[0],
            is_public=False,
            agent_speaks_first=False,
            tools=[
                tool.tool_id
            ]
        )

        # Create context
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Create request
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hello! What's the weather in Melbourne?"
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
        print(response)

        # Clean up
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)
        Tool.delete_tool(tool.tool_id)
        Agent.delete_agent(agent.agent_id)
        Context.delete_context(context.context_id)

    def test_agent_with_tool_with_passed_context(self):

        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create tool
        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="get_context",
            description="Returns the context",
            code="def get_context(context):\n  return json.dumps(context)",
            pd_id=None,  # No parameters needed for this tool
            pass_context=True
        )

        # Create agent
        agent: Agent.Agent = Agent.create_agent(
            agent_name="Context Agent",
            agent_description="Can return the context passed to it",
            prompt="When the user asks for the context, call the get_context tool and return the exact contents of it",
            org_id=user.organizations[0],
            is_public=False,
            agent_speaks_first=False,
            tools=[
                tool.tool_id
            ]
        )

        # Create context
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id,
        )

        # Create request
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hello! What's the context?"
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
        print(response)

        # Clean up
        Tool.delete_tool(tool.tool_id)
        Agent.delete_agent(agent.agent_id)
        Context.delete_context(context.context_id)

    def test_create_agent_with_prompt_arg_names_new_style(self):
        """Test creating an agent with new ARG_* style prompt_arg_names (no brackets)"""
        
        # Create agent with ARG_* style prompt_arg_names
        create_agent_body = {
            "agent_name": "Test Agent with Args",
            "agent_description": "Test Description",
            "prompt": "Hello ARG_USER_NAME, you are located in ARG_LOCATION",
            "is_public": False,
            "agent_speaks_first": False,
            "uses_prompt_args": True,
            "prompt_arg_names": ["ARG_USER_NAME", "ARG_LOCATION"]
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

        # Check for prompt_arg_names
        self.assertEqual(res_body["prompt_arg_names"], ["ARG_USER_NAME", "ARG_LOCATION"])
        self.assertEqual(res_body["uses_prompt_args"], True)

        # Clean up
        Agent.delete_agent(res_body["agent_id"])

    def test_create_agent_with_prompt_arg_names_legacy_style(self):
        """Test creating an agent with legacy {name} style - brackets included in arg names"""
        
        # Create agent with legacy style - note: brackets are PART of the arg name
        create_agent_body = {
            "agent_name": "Test Agent Legacy Style",
            "agent_description": "Test Description",
            "prompt": "Hello {name}, you are located in {location}",
            "is_public": False,
            "agent_speaks_first": False,
            "uses_prompt_args": True,
            "prompt_arg_names": ["{name}", "{location}"]  # Brackets included!
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

        # Check for prompt_arg_names - brackets should be preserved
        self.assertEqual(res_body["prompt_arg_names"], ["{name}", "{location}"])

        # Clean up
        Agent.delete_agent(res_body["agent_id"])

    def test_agent_with_prompt_args_and_json_in_prompt(self):
        """Test that prompt args work correctly when prompt contains JSON examples"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create agent with JSON in prompt and prompt_arg_names using NEW style (ARG_*)
        # This demonstrates that JSON curly brackets are NOT affected
        prompt_with_json = """You are an assistant for ARG_USER_NAME.

When responding with data, use this JSON format:
{"status": "success", "data": {"key": "value"}}

Always include the user's name in responses."""

        agent = Agent.create_agent(
            agent_name="JSON Prompt Agent",
            agent_description="Agent with JSON in prompt",
            prompt=prompt_with_json,
            org_id=user.organizations[0],
            is_public=False,
            agent_speaks_first=False,
            uses_prompt_args=True,
            prompt_arg_names=["ARG_USER_NAME"]
        )

        # Create context with prompt_args
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id,
            prompt_args={"ARG_USER_NAME": "Alice"}
        )

        # Create a chat request
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hello! What's my name?"
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda function - this should NOT error due to JSON curly brackets
        result = lambda_handler(request, None)

        # Check the response - should be 200 (not a format error)
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        self.assertIn("response", response)
        # The response should mention Alice since that's the user_name arg
        print(f"Response: {response['response']}")

        # Clean up
        Agent.delete_agent(agent.agent_id)
        Context.delete_context(context.context_id)

    def test_agent_with_legacy_prompt_args_and_json_in_prompt(self):
        """Test legacy {name} style with JSON in prompt - brackets included in arg names"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create agent with JSON in prompt using LEGACY style
        # The {user_name} will be replaced, but {"status": ...} won't be because
        # only the exact strings in prompt_arg_names are replaced
        prompt_with_json = """You are an assistant for {user_name}.

When responding with data, use this JSON format:
{"status": "success", "data": {"key": "value"}}

Always include the user's name in responses."""

        agent = Agent.create_agent(
            agent_name="JSON Prompt Agent Legacy",
            agent_description="Agent with JSON in prompt - legacy style",
            prompt=prompt_with_json,
            org_id=user.organizations[0],
            is_public=False,
            agent_speaks_first=False,
            uses_prompt_args=True,
            prompt_arg_names=["{user_name}"]  # Brackets included!
        )

        # Create context with prompt_args - key includes brackets to match
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id,
            prompt_args={"{user_name}": "Bob"}  # Key matches the prompt_arg_name
        )

        # Create a chat request
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hello! What's my name?"
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda function - JSON should be preserved
        result = lambda_handler(request, None)

        # Check the response - should be 200
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        self.assertIn("response", response)
        print(f"Response: {response['response']}")

        # Clean up
        Agent.delete_agent(agent.agent_id)
        Context.delete_context(context.context_id)

    def test_agent_with_prompt_arg_names_backwards_compatibility(self):
        """Test that agents without prompt_arg_names still work (backwards compatibility)"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create agent without prompt_arg_names (old style)
        agent = Agent.create_agent(
            agent_name="Old Style Agent",
            agent_description="Agent without prompt_arg_names",
            prompt="You are a helpful assistant.",
            org_id=user.organizations[0],
            is_public=False,
            agent_speaks_first=False
            # Note: no prompt_arg_names specified
        )

        # Verify prompt_arg_names defaults to empty list
        self.assertEqual(agent.prompt_arg_names, [])

        # Create context
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Create a chat request - should work without errors
        request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Hello!"
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda function
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # Clean up
        Agent.delete_agent(agent.agent_id)
        Context.delete_context(context.context_id)

    def test_update_agent_with_prompt_arg_names(self):
        """Test updating an agent's prompt_arg_names"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            agent_name="Test Agent",
            agent_description="Test Description",
            prompt="Hello ARG_NAME from ARG_CITY",
            org_id=user.organizations[0],
            is_public=False,
            agent_speaks_first=False,
            uses_prompt_args=True,
            prompt_arg_names=["ARG_NAME"]  # Initially only has ARG_NAME
        )

        # Update to add ARG_CITY to prompt_arg_names
        update_agent_body = {
            "prompt_arg_names": ["ARG_NAME", "ARG_CITY"]
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

        # Check for updated prompt_arg_names
        self.assertEqual(res_body["prompt_arg_names"], ["ARG_NAME", "ARG_CITY"])

        # Clean up
        Agent.delete_agent(agent.agent_id)

    