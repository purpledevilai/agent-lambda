import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
# Imports for test
from src.AWS import Cognito
from src.Models import Organization
from src.Models import User


class TestOrganization(unittest.TestCase):


    def test_create_organization(self):

        # Create org data
        organization_name = "My Organization"
        organization_body = {
            "name": organization_name
        }

        # Create request
        request = create_request(
            method="POST",
            path="/organization",
            headers={
                "Authorization": access_token
            },
            body=organization_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["name"], organization_name)

        # Check for user id in org user
        cognitoUser: Cognito.CognitoUser = Cognito.get_user_from_cognito(access_token)
        self.assertIn(cognitoUser.sub, res_body["users"])

        # Check for org_id in user
        user: User.User = User.get_user(cognitoUser.sub)
        self.assertIn(res_body["org_id"], user.organizations)

        # Clean up
        Organization.delete_organization(res_body["org_id"])
        user.organizations.remove(res_body["org_id"])
        User.save_user(user)
        