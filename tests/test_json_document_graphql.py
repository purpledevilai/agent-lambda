import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
from src.Models import JSONDocument, User
from src.AWS import Cognito


class TestJSONDocumentGraphQL(unittest.TestCase):
    def setUp(self):
        cognito_user = Cognito.get_user_from_cognito(access_token)
        self.user = User.get_user(cognito_user.sub)
        self.document = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=self.user.organizations[0],
                data={"name": "Doc", "value": {"a": 1}},
            )
        )

    def tearDown(self):
        JSONDocument.delete_json_document(self.document.document_id)

    def test_view_schema(self):
        request = create_request(
            method="GET",
            path=f"/json-document/{self.document.document_id}/schema",
        )
        response = lambda_handler(request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertIn("type Query", body["schema"])

    def test_graphql_query_and_mutation(self):
        query_request = create_request(
            method="POST",
            path=f"/json-document/{self.document.document_id}/graphql",
            headers={"Authorization": access_token},
            body={"query": "{ name }"},
        )
        response = lambda_handler(query_request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["data"]["name"], "Doc")

        mutation = "mutation{ update(path:\"name\", value:\"\\\"New\\\"\"){ name }}"
        mutate_request = create_request(
            method="POST",
            path=f"/json-document/{self.document.document_id}/graphql",
            headers={"Authorization": access_token},
            body={"query": mutation},
        )
        mutate_response = lambda_handler(mutate_request, None)
        self.assertEqual(mutate_response["statusCode"], 200)
        mutate_body = json.loads(mutate_response["body"])
        self.assertEqual(mutate_body["data"]["update"]["name"], "New")

        updated_doc = JSONDocument.get_json_document(self.document.document_id)
        self.assertEqual(updated_doc.data["name"], "New")

    def test_mutate_endpoint(self):
        request = create_request(
            method="POST",
            path=f"/json-document/{self.document.document_id}/mutate",
            headers={"Authorization": access_token},
            body={"path": "value.a", "value": 2},
        )
        response = lambda_handler(request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["data"]["value"]["a"], 2)

