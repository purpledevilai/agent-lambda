import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token, agent_id_outside_of_org
from src.lambda_function import lambda_handler
# Import for test
from src.Models import Context, Agent, User
from src.AWS import Cognito


class TestContext(unittest.TestCase):

    def test_create_context(self):

        # Create org data
        agent_id = "aj"
        create_context_body = {
            "agent_id": agent_id
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_id"], agent_id)

        # Clean up
        Context.delete_context(res_body["context_id"])

    def test_create_public_context(self):

        # Create org data
        public_agent_id = "aj-public"
        create_context_body = {
            "agent_id": public_agent_id,
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_id"], public_agent_id)

        # Clean up
        Context.delete_context(res_body["context_id"])

    def test_create_context_for_non_public_agent(self):

        # Create org data
        non_public_agent_id = "aj"
        create_context_body = {
            "agent_id": non_public_agent_id
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 403)

    def test_create_context_for_an_outside_agent(self):

        # Create org data
        create_context_body = {
            "agent_id": agent_id_outside_of_org
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)
        print(result)

        # Check the response
        self.assertEqual(result["statusCode"], 403)

        

    def test_get_context(self):

        cognito_user = Cognito.get_user_from_cognito(access_token)
        context = Context.create_context("aj", cognito_user.sub)

        # Create request
        request = create_request(
            method="GET",
            path=f"/context/{context.context_id}",
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
        self.assertEqual(res_body["agent_id"], "aj")

        # Clean up
        Context.delete_context(context.context_id)

    def test_get_public_context(self):

        context: Context.Context = Context.create_context("aj-public", None)

        # Create request
        request = create_request(
            method="GET",
            path=f"/context/{context.context_id}"
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_id"], "aj-public")

        # Clean up
        Context.delete_context(context.context_id)

    def test_delete_context(self):

        cognito_user = Cognito.get_user_from_cognito(access_token)
        context = Context.create_context("aj", cognito_user.sub)

        # Create request
        request = create_request(
            method="DELETE",
            path=f"/context/{context.context_id}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        self.assertEqual(res_body["success"], True)

    def test_get_context_history(self):

        cognito_user = Cognito.get_user_from_cognito(access_token)
        context = Context.create_context("aj", cognito_user.sub)

        # Create request
        request = create_request(
            method="GET",
            path="/context-history",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        self.assertGreaterEqual(len(res_body["contexts"]), 1)

        # Clean up
        Context.delete_context(context.context_id)

    def test_create_context_with_prompt_args(self):

        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent("aj", "agent with prompt args", "Say hello to {name}", user.organizations[0], False, True)

        create_context_body = {
            "agent_id": agent.agent_id,
            "prompt_args": {
                "name": "Alice"
            }
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        res_body = json.loads(result["body"])

        # Check for name in the first message
        self.assertTrue("Alice" in res_body["messages"][0]["message"])

        # Clean up
        Context.delete_context(res_body["context_id"])
        Agent.delete_agent(agent.agent_id)
