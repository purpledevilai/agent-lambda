from src.Models import StructuredResponseEndpoint as SRE, ParameterDefinition, User
from src.AWS import Cognito
from src.lambda_function import lambda_handler
from tests.config import access_token
from tests.helper_funcs import create_request
import json
import unittest
import sys
sys.path.append("../")
# Import for test


class TestSRE(unittest.TestCase):

    def test_create_sre(self):
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
            path="/sre",
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
        self.assertEqual(result["prompt_template"], "{prompt}")

        # Clean up
        SRE.delete_sre(result["sre_id"])
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_get_sre(self):
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

        sre = SRE.create_sre(
            org_id=user.organizations[0],
            name="Extract People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="GET",
            path=f"/sre/{sre.sre_id}",
            headers={
                "Authorization": access_token
            },
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

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

        sre = SRE.create_sre(
            org_id=user.organizations[0],
            name="Extract People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="POST",
            path=f"/sre/{sre.sre_id}",
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
        SRE.delete_sre(sre.sre_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_delete_sre(self):
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

        sre = SRE.create_sre(
            org_id=user.organizations[0],
            name="Extract People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="DELETE",
            path=f"/sre/{sre.sre_id}",
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

        self.assertTrue(SRE.sre_exists(sre.sre_id) is False)

        # Clean up
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_get_sres(self):
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

        sre = SRE.create_sre(
            org_id=user.organizations[0],
            name="Extract People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="GET",
            path="/sres",
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

        self.assertGreaterEqual(len(result["sres"]), 1)

        # Clean up
        SRE.delete_sre(sre.sre_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_run_sre(self):
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

        sre = SRE.create_sre(
            org_id=user.organizations[0],
            name="Extract_People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="POST",
            path=f"/run-sre/{sre.sre_id}",
            headers={
                "Authorization": access_token
            },
            body={
                "prompt": "My name is John Doe and I live in New York with my sister Jane Doe. We have a cousing named John Smith."
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
        SRE.delete_sre(sre.sre_id)
        ParameterDefinition.delete_parameter_definition(pd.pd_id)

    def test_run_sre_with_enum_param_def(self):
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

        sre = SRE.create_sre(
            org_id=user.organizations[0],
            name="Extract_People",
            description="Extracts people from a text with name and age enum",
            pd_id=pd.pd_id,
        )

        # Create request
        request = create_request(
            method="POST",
            path=f"/run-sre/{sre.sre_id}",
            headers={
                "Authorization": access_token
            },
            body={
                "prompt": "My name is John Doe and I live in New York with my sister Jane Doe. We have a cousin named John Smith."
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Clean up
        ParameterDefinition.delete_parameter_definition(pd.pd_id)
        SRE.delete_sre(sre.sre_id)

        # Check the response
        self.assertEqual(response["statusCode"], 200)

        

    def test_run_sre_missing_argument(self):
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

        sre = SRE.create_sre(
            org_id=user.organizations[0],
            name="Extract_People",
            description="Extracts people from a text",
            pd_id=pd.pd_id,
            prompt_template="Summarize {article}"
        )

        request = create_request(
            method="POST",
            path=f"/run-sre/{sre.sre_id}",
            headers={"Authorization": access_token},
            body={"prompt": "unused"}
        )

        response = lambda_handler(request, None)
        self.assertEqual(response["statusCode"], 400)

        ParameterDefinition.delete_parameter_definition(pd.pd_id)
        SRE.delete_sre(sre.sre_id)
