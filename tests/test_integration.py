import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
from src.AWS import Cognito
from src.Models import Integration, User


class TestIntegration(unittest.TestCase):
    def test_create_integration(self):
        request = create_request(
            method="POST",
            path="/integration",
            headers={"Authorization": access_token},
            body={"type": "jira", "integration_config": {"token": "abc"}},
        )
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        body = json.loads(result["body"])
        self.assertEqual(body["type"], "jira")
        Integration.delete_integration(body["integration_id"])

    def test_read_integration(self):
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        integration = Integration.create_integration(
            org_id=user.organizations[0],
            type="jira",
            integration_config={"token": "a"},
        )
        request = create_request(
            method="GET",
            path=f"/integration/{integration.integration_id}",
            headers={"Authorization": access_token},
        )
        response = lambda_handler(request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["integration_id"], integration.integration_id)
        Integration.delete_integration(integration.integration_id)

    def test_update_integration(self):
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        integration = Integration.create_integration(
            org_id=user.organizations[0],
            type="jira",
            integration_config={"token": "a"},
        )
        request = create_request(
            method="POST",
            path=f"/integration/{integration.integration_id}",
            headers={"Authorization": access_token},
            body={"integration_config": {"token": "b"}},
        )
        response = lambda_handler(request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["integration_config"]["token"], "b")
        Integration.delete_integration(integration.integration_id)

    def test_delete_integration(self):
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        integration = Integration.create_integration(
            org_id=user.organizations[0],
            type="jira",
            integration_config={},
        )
        request = create_request(
            method="DELETE",
            path=f"/integration/{integration.integration_id}",
            headers={"Authorization": access_token},
        )
        response = lambda_handler(request, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertFalse(Integration.integration_exists(integration.integration_id))

    def test_get_integrations(self):
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        integration = Integration.create_integration(
            org_id=user.organizations[0],
            type="jira",
            integration_config={},
        )
        request = create_request(
            method="GET",
            path="/integrations",
            headers={"Authorization": access_token},
        )
        response = lambda_handler(request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertTrue(len(body) > 0)
        Integration.delete_integration(integration.integration_id)
