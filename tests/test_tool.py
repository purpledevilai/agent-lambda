from src.lambda_function import lambda_handler
from tests.config import access_token
from tests.helper_funcs import create_request
import json
import unittest
import sys
sys.path.append("../")
# Import for test
from src.AWS import Cognito
from src.Models import Agent, Tool, ParameterDefinition, User


class TestTool(unittest.TestCase):

    def test_create_tool(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        parameter_definition = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "test_string",
                    "description": "test",
                    "type": "string",
                }
            ]
        )

        # Create the request
        request = create_request(
            method="POST",
            path="/tool",
            headers={
                "Authorization": access_token
            },
            body={
                "name": "Test Tool",
                "description": "Test",
                "pd_id": f"{parameter_definition.pd_id}",
                "code": "def test():\n  return 'test'",
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # parse result
        result = json.loads(result["body"])

        self.assertEqual(result["name"], "Test Tool")

        # Clean up
        Tool.delete_tool(result["tool_id"])
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)

    def test_create_tool_no_pd_id(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create the request
        request = create_request(
            method="POST",
            path="/tool",
            headers={
                "Authorization": access_token
            },
            body={
                "name": "Test Tool",
                "description": "Test",
                "code": "def test():\n  return 'test'",
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # parse result
        result = json.loads(result["body"])

        self.assertEqual(result["name"], "Test Tool")
        self.assertIsNone(result["pd_id"])

        # Clean up
        Tool.delete_tool(result["tool_id"])

    def test_read_tool(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        parameter_definition = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "test_string",
                    "description": "test",
                    "type": "string",
                }
            ]
        )

        # Create the tool
        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="Test Tool",
            description="Test",
            pd_id=parameter_definition.pd_id,
            code="def test():\n  return 'test'"
        )

        # Create the request
        request = create_request(
            method="GET",
            path=f"/tool/{tool.tool_id}",
            headers={
                "Authorization": access_token
            },
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check the response body
        self.assertEqual(body["tool_id"], tool.tool_id)

        # Clean up
        Tool.delete_tool(tool.tool_id)
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)

    def test_update_tool(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        parameter_definition = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "test_string",
                    "description": "test",
                    "type": "string",
                }
            ]
        )

        # Create the tool
        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="Test Tool",
            description="Test",
            pd_id=parameter_definition.pd_id,
            code="def test():\n  return 'test'"
        )

        # Create the request
        request = create_request(
            method="POST",
            path=f"/tool/{tool.tool_id}",
            headers={
                "Authorization": access_token
            },
            body={
                "name": "Updated Tool",
                "description": "Updated",
                "pd_id": f"{parameter_definition.pd_id}",
                "code": "def test():\n  return 'updated'",
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check the response body
        self.assertEqual(body["name"], "Updated Tool")

        # Clean up
        Tool.delete_tool(tool.tool_id)
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)

    def test_update_tool_no_pd_id(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        parameter_definition = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "test_string",
                    "description": "test",
                    "type": "string",
                }
            ]
        )

        # Create the tool
        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="Test Tool",
            description="Test",
            pd_id=parameter_definition.pd_id,
            code="def test():\n  return 'test'"
        )

        # Create the request
        request = create_request(
            method="POST",
            path=f"/tool/{tool.tool_id}",
            headers={
                "Authorization": access_token
            },
            body={
                "name": "Updated Tool",
                "description": "Updated",
                "code": "def test():\n  return 'updated'",
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check the response body
        self.assertIsNone(body["pd_id"])

        # Clean up
        Tool.delete_tool(tool.tool_id)
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)

    def test_delete_tool(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        parameter_definition = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "test_string",
                    "description": "test",
                    "type": "string",
                }
            ]
        )

        # Create the tool
        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="Test Tool",
            description="Test",
            pd_id=parameter_definition.pd_id,
            code="def test():\n  return 'test'"
        )

        # Create the request
        request = create_request(
            method="DELETE",
            path=f"/tool/{tool.tool_id}",
            headers={
                "Authorization": access_token
            },
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        # Check the tool is deleted
        self.assertFalse(Tool.tool_exists(tool.tool_id))

        # Clean up
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)

    def test_list_tools(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        parameter_definition = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "test_string",
                    "description": "test",
                    "type": "string",
                }
            ]
        )

        # Create the tool
        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="Test Tool",
            description="Test",
            pd_id=parameter_definition.pd_id,
            code="def test():\n  return 'test'"
        )

        # Create the request
        request = create_request(
            method="GET",
            path="/tools",
            headers={
                "Authorization": access_token
            },
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check the response body
        self.assertTrue(len(body) > 0)

        # Clean up
        Tool.delete_tool(tool.tool_id)
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)


    def test_test_tool(self):

        # Create request
        request = create_request(
            method="POST",
            path=f"/test-tool",
            headers={
                "Authorization": access_token
            },
            body={
                "function_name": "get_weather",
                "code": "def get_weather(lat, long):\n  url = f\"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current=temperature_2m\"\n\n  try:\n    data = requests.get(url).json()\n    return data[\"current\"][\"temperature_2m\"]  # Extract temperature\n  except Exception as e:\n    return f\"Error fetching temperature: {e}\"",
                "params": {
                    "lat": -37.8136,
                    "long": 144.9631
                }
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # parse result
        result = json.loads(result["body"])

        print(result)

    def test_hack_code(self):
        hack_code = """
# import boto3 # cant import anyways


def try_aws_access():
    results = {}

    # Try listing IAM users
    try:
        iam_client = boto3.client("iam")
        users = iam_client.list_users()
        results["IAM Users"] = users
    except Exception as e:
        results["IAM Users"] = f"Blocked: {e}"

    # Try accessing DynamoDB (replace 'YourTableName' with an actual table)
    try:
        dynamodb = boto3.client("dynamodb")
        response = dynamodb.scan(TableName="agents")
        results["DynamoDB Scan"] = response
    except Exception as e:
        results["DynamoDB Scan"] = f"Blocked: {e}"

    # Try accessing Cognito User Pool (replace with actual user pool ID)
    try:
        cognito = boto3.client("cognito-idp")
        response = cognito.list_users(UserPoolId="us-east-1_YourUserPoolId")
        results["Cognito Users"] = response
    except Exception as e:
        results["Cognito Users"] = f"Blocked: {e}"

    # Try reading environment variables
    try:
        env_vars = dict(os.environ)
        results["Environment Variables"] = env_vars
    except Exception as e:
        results["Environment Variables"] = f"Blocked: {e}"

    # Try writing to the file system
    try:
        with open("/tmp/hacked.txt", "w") as f:
            f.write("This should not be possible!")
        results["File System Write"] = "Success! Check /tmp/hacked.txt"
    except Exception as e:
        results["File System Write"] = f"Blocked: {e}"

    try:
        os.system("ls")  # Should be blocked
        results["OS Command Execution"] = "Success! Check the logs"
    except Exception as e:
        results["OS Command Execution"] = f"Blocked OS access: {e}"

    return json.dumps(results)
"""
        # Create request
        request = create_request(
            method="POST",
            path=f"/test-tool",
            headers={
                "Authorization": access_token
            },
            body={
                "function_name": "try_aws_access",
                "code": hack_code,
                "params": {}
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # parse result
        body = json.loads(result["body"])

        # parse result in body
        body_result = json.loads(body["result"])

        # Check that all keys in the body_result have the word "Blocked"
        for key in body_result:
            self.assertIn("Blocked", body_result[key])

        print(body_result)

    def test_get_tools_for_agent(self):

        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create the tool
        tool: Tool.Tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="Test Tool",
            description="Test",
            code="def test():\n  return 'test'"
        )

        # Create Agent
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="Test Agent",
            agent_description="Test",
            prompt="Test",
            is_public=False,
            agent_speaks_first=False,
            tools=[tool.tool_id]
        )

        # Create the request
        request = create_request(
            method="GET",
            path="/tools",
            query_string_parameters={
                "agent_id": agent.agent_id
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check the response body
        self.assertTrue(len(body["tools"]) > 0)
        self.assertEqual(body["tools"][0]["tool_id"], tool.tool_id)

        # Clean up
        Tool.delete_tool(tool.tool_id)
        Agent.delete_agent(agent.agent_id)

