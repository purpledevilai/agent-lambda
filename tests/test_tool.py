from src.lambda_function import lambda_handler
from tests.config import access_token
from tests.helper_funcs import create_request
import json
import unittest
import sys
sys.path.append("../")
# Import for test


class TestTool(unittest.TestCase):

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
