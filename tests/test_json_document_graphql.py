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
                data={
                    "note1": "This is a test note",
                    "People": [
                        {
                            "name": "Bob",
                            "age": 30,
                            "city": "Wonderland",
                            "is_active": True
                        },
                        {
                            "name": "Alice",
                            "age": 28,
                            "city": "Dreamland",
                            "is_active": False
                        }
                    ]
                },
                is_public=True
            )
        )

    def tearDown(self):
        JSONDocument.delete_json_document(self.document.document_id)

    def test_get_document_schema(self):
        # Test public document schema without authentication
        request = create_request(
            method="GET",
            path=f"/json-document/{self.document.document_id}/schema",
            # No auth headers for public document
        )
        response = lambda_handler(request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        print(json.dumps(body, indent=2))
        self.assertIn("type Query", body["schema"])
        # Verify the schema contains the structure of our document
        self.assertIn("People", body["schema"])

    def test_graphql_query(self):
        query_request = create_request(
            method="POST",
            path=f"/json-document/{self.document.document_id}/graphql",
            headers={"Authorization": access_token},
            body={"query": "{ People { name age is_active } }"},
        )
        response = lambda_handler(query_request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        print(json.dumps(body, indent=2))
        self.assertEqual(body["data"]["People"][0]["name"], "Bob")
        self.assertEqual(body["data"]["People"][0]["age"], 30)
        self.assertEqual(body["data"]["People"][0]["is_active"], True)
        # assert that city is not included in the query result
        self.assertNotIn("city", body["data"]["People"][0])

    def test_graphql_mutation(self):
        # Update Bob's age with a mutation
        mutation = """mutation { 
            update(path: "People.0.age", value: "35") { 
                People { 
                    name 
                    age 
                    city 
                } 
            } 
        }"""
        
        mutate_request = create_request(
            method="POST",
            path=f"/json-document/{self.document.document_id}/graphql",
            headers={"Authorization": access_token},
            body={"query": mutation},
        )
        mutate_response = lambda_handler(mutate_request, None)
        self.assertEqual(mutate_response["statusCode"], 200)
        mutate_body = json.loads(mutate_response["body"])
        self.assertEqual(mutate_body["data"]["update"]["People"][0]["age"], 35)

        # Verify the document was updated in the database
        updated_doc = JSONDocument.get_json_document(self.document.document_id)
        self.assertEqual(updated_doc.data["People"][0]["age"], 35)

    def test_document_mutate_endpoint(self):
        # Add a new person to the People array
        request = create_request(
            method="POST",
            path=f"/json-document/{self.document.document_id}/mutate",
            headers={"Authorization": access_token},
            body={
                "path": "People.1", 
                "value": {
                    "name": "Alice",
                    "age": 28,
                    "city": "Dreamland"
                }
            },
        )
        response = lambda_handler(request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        
        # Verify the data was updated correctly
        self.assertEqual(body["data"]["People"][1]["name"], "Alice")
        self.assertEqual(body["data"]["People"][1]["age"], 28)
        self.assertEqual(body["data"]["People"][1]["city"], "Dreamland")
        
        # Verify the original data is still intact
        self.assertEqual(body["data"]["note1"], "This is a test note")
        self.assertEqual(body["data"]["People"][0]["name"], "Bob")

    def test_public_document_graphql_query(self):
        # Test accessing a public document's GraphQL endpoint without auth
        query_request = create_request(
            method="POST",
            path=f"/json-document/{self.document.document_id}/graphql",
            # No auth headers
            body={"query": "{ note1 People { name } }"},
        )
        response = lambda_handler(query_request, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["data"]["note1"], "This is a test note")
        self.assertEqual(body["data"]["People"][0]["name"], "Bob")

