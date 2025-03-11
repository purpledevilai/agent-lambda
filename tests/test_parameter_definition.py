import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
# Import for test
from src.AWS import Cognito
from src.Models import ParameterDefinition, User

class TestParameterDefinition(unittest.TestCase):
    
    def test_create_parameter_definition(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create the request
        request = create_request(
            method="POST",
            path="/parameter-definition",
            headers={
                "Authorization": access_token
            },
            body={
                "parameters": [
                    {
                        "name": "test_string",
                        "description": "test",
                        "type": "string",
                    },
                    {
                        "name": "test_number",
                        "description": "test",
                        "type": "number",
                    },
                    {
                        "name": "test_boolean",
                        "description": "test",
                        "type": "boolean",
                    },
                    {
                        "name": "test_object",
                        "description": "test",
                        "type": "object",
                        "parameters": [
                            {
                                "name": "test_string",
                                "description": "test",
                                "type": "string",
                            },
                            {
                                "name": "test_object_2",
                                "description": "test",
                                "type": "object",
                                "parameters": [
                                    {
                                        "name": "test_string",
                                        "description": "test",
                                        "type": "string",
                                    }
                                ]
                            },
                            {
                                "name": "test_array",
                                "description": "test",
                                "type": "array",
                                "parameters": [
                                    {
                                        "name": "test_number",
                                        "description": "test",
                                        "type": "number",
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "test_array",
                        "description": "test",
                        "type": "array",
                        "parameters": [
                            {
                                "name": "test_object",
                                "description": "test",
                                "type": "object",
                                "parameters": [
                                    {
                                        "name": "test_string_1",
                                        "description": "test",
                                        "type": "string",
                                    },
                                    {
                                        "name": "test_string_2",
                                        "description": "test",
                                        "type": "string",
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "test_enum",
                        "description": "test",
                        "type": "enum",
                    }
                ]
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check the response body
        self.assertTrue("pd_id" in body)

        # Clean up
        ParameterDefinition.delete_parameter_definition(body["pd_id"])


    def test_read_parameter_definition(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create the parameter definition
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
            method="GET",
            path=f"/parameter-definition/{parameter_definition.pd_id}",
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
        self.assertEqual(body["pd_id"], parameter_definition.pd_id)

        # Clean up
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)

    def test_update_parameter_definition(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create the parameter definition
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
            path=f"/parameter-definition/{parameter_definition.pd_id}",
            headers={
                "Authorization": access_token
            },
            body={
                "parameters": [
                    {
                        "name": "test_number",
                        "description": "test",
                        "type": "number",
                    }
                ]
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check we updated the parameter definition
        self.assertEqual(body["parameters"][0]["type"], "number")

        # Clean up
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)

    def test_delete_parameter_definition(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create the parameter definition
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
            method="DELETE",
            path=f"/parameter-definition/{parameter_definition.pd_id}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        # Check the parameter definition was deleted
        self.assertFalse(ParameterDefinition.parameter_definition_exists(parameter_definition.pd_id))

    def test_get_parameter_definitions(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create the parameter definition
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
            method="GET",
            path="/parameter-definitions",
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
        self.assertTrue(len(body) > 0)

        # Clean up
        ParameterDefinition.delete_parameter_definition(parameter_definition.pd_id)