from src.Models import SingleMessageEndpoint as SME, ParameterDefinition, User
from src.AWS import Cognito
from src.lambda_function import lambda_handler
from tests.config import access_token
from tests.helper_funcs import create_request
import json
import unittest
import sys
sys.path.append("../")
# Import for test


class TestSME(unittest.TestCase):

    def test_create_sme(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "people",
                    "description": "people",
                    "type": "array",
                    "parameters": [
                        {
                            "name": "name",
                            "description": "name",
                            "type": "string",
                            "parameters": []
                        }
                    ]
                }
            ]
        )

        # Create request
        request = create_request(
            method="POST",
            path="/sme",
            headers={
                "Authorization": access_token
            },
            body={
                "name": "Extract People",
                "description": "Extracts people from a text",
                "pd_id": pd.pd_id,
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        # Parse result
        result = json.loads(response["body"])

        self.assertEqual(result["name"], "Extract People")
        self.assertEqual(result["pd_id"], pd.pd_id)

        # Clean up
        SME.delete_sme(result["sme_id"])
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_get_sme(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "people",
                    "description": "people",
                    "type": "array",
                    "parameters": [
                        {
                            "name": "name",
                            "description": "name",
                            "type": "string",
                            "parameters": []
                        }
                    ]
                }
            ]
        )

        sme = SME.create_sme(
            org_id=user.organizations[0],
            name="Extract People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="GET",
            path=f"/sme/{sme.sme_id}",
            headers={
                "Authorization": access_token
            },
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        # Parse result
        result = json.loads(response["body"])

        self.assertEqual(result["name"], "Extract People")
        self.assertEqual(result["pd_id"], pd.pd_id)

        # Clean up
        SME.delete_sme(sme.sme_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_update_sme(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "people",
                    "description": "people",
                    "type": "array",
                    "parameters": [
                        {
                            "name": "name",
                            "description": "name",
                            "type": "string",
                            "parameters": []
                        }
                    ]
                }
            ]
        )

        sme = SME.create_sme(
            org_id=user.organizations[0],
            name="Extract People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="POST",
            path=f"/sme/{sme.sme_id}",
            headers={
                "Authorization": access_token
            },
            body={
                "description": "Extracts people from a text and their age"
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        # Parse result
        result = json.loads(response["body"])
        print(result)

        self.assertEqual(result["description"],
                         "Extracts people from a text and their age")

        # Clean up
        SME.delete_sme(sme.sme_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_delete_sme(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "people",
                    "description": "people",
                    "type": "array",
                    "parameters": [
                        {
                            "name": "name",
                            "description": "name",
                            "type": "string",
                            "parameters": []
                        }
                    ]
                }
            ]
        )

        sme = SME.create_sme(
            org_id=user.organizations[0],
            name="Extract People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="DELETE",
            path=f"/sme/{sme.sme_id}",
            headers={
                "Authorization": access_token
            },
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        # Parse result
        result = json.loads(response["body"])

        self.assertTrue(SME.sme_exists(sme.sme_id) is False)

        # Clean up
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_get_smes(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "people",
                    "description": "people",
                    "type": "array",
                    "parameters": [
                        {
                            "name": "name",
                            "description": "name",
                            "type": "string",
                            "parameters": []
                        }
                    ]
                }
            ]
        )

        sme = SME.create_sme(
            org_id=user.organizations[0],
            name="Extract People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="GET",
            path="/smes",
            headers={
                "Authorization": access_token
            },
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        # Parse result
        result = json.loads(response["body"])
        print(result)

        self.assertGreaterEqual(len(result["smes"]), 1)

        # Clean up
        SME.delete_sme(sme.sme_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_run_sme(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "people",
                    "description": "people",
                    "type": "array",
                    "parameters": [
                        {
                            "name": "name",
                            "description": "name",
                            "type": "string",
                            "parameters": []
                        }
                    ]
                }
            ]
        )

        sme = SME.create_sme(
            org_id=user.organizations[0],
            name="Extract_People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="POST",
            path=f"/run-sme/{sme.sme_id}",
            headers={
                "Authorization": access_token
            },
            body={
                "message": "My name is John Doe and I live in New York with my sister Jane Doe. We have a cousing named John Smith."
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        # Parse result
        result = json.loads(response["body"])
        print(result)

        self.assertGreater(len(result["people"]), 0)

        # Clean up
        SME.delete_sme(sme.sme_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_run_sme_with_enum_param_def(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        pd = ParameterDefinition.create_parameter_definition(
            org_id=user.organizations[0],
            parameters=[
                {
                    "name": "people",
                    "description": "The extracted people",
                    "type": "array",
                    "parameters": [
                        {
                            "name": "person",
                            "description": "object representing a person",
                            "type": "object",
                            "parameters": [
                                {
                                    "name": "name",
                                    "description": "Name of the person",
                                    "type": "string",
                                    "parameters": []
                                },
                                {
                                    "name": "age",
                                    "description": "Age of the person",
                                    "type": "enum",
                                    "parameters": [
                                        {
                                            "name": "young",
                                            "type": "string",
                                            "description": "young"
                                        },
                                        {
                                            "name": "old",
                                            "type": "string",
                                            "description": "old"
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                }
            ]
        )

        sme = SME.create_sme(
            org_id=user.organizations[0],
            name="Extract_People",
            description="Extracts people from a text with name and age enum",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="POST",
            path=f"/run-sme/{sme.sme_id}",
            headers={
                "Authorization": access_token
            },
            body={
                "message": "My name is John Doe and I live in New York with my sister Jane Doe. We have a cousin named John Smith."
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Clean up
        ParameterDefinition.delete_parameter_definition(pd.pd_id)
        SME.delete_sme(sme.sme_id)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        
