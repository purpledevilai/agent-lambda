import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
# Imports for test
from src.Models import JSONDocument, User
from src.AWS import Cognito


class TestJSONDocuments(unittest.TestCase):

    def test_create_json_document(self):
        # Create request
        request = create_request(
            method="POST",
            path="/json-document",
            headers={
                "Authorization": access_token
            },
            body={
                "data": {
                    "note1": "This is a test note",
                    "People": [
                        { "name": "Alice"},
                        {
                            "name": "Bob",
                            "age": 30,
                            "city": "Wonderland"
                        }
                    ]
                },
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200, "Expected status code 200")

        res_body = json.loads(result["body"])

        print("Response Body:", json.dumps(res_body, indent=2))

        # Clean up
        document_id = res_body["document_id"]
        JSONDocument.delete_json_document(document_id)
        
    def test_read_json_document(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create a JSON document for testing
        json_document = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                data={
                    "test_key": "test_value",
                    "nested": {
                        "field1": "value1",
                        "field2": 42
                    }
                }
            )
        )

        # Create the request
        request = create_request(
            method="GET",
            path=f"/json-document/{json_document.document_id}",
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
        self.assertEqual(body["document_id"], json_document.document_id)
        self.assertEqual(body["data"]["test_key"], "test_value")
        self.assertEqual(body["data"]["nested"]["field2"], 42)

        # Clean up
        JSONDocument.delete_json_document(json_document.document_id)
        
    def test_update_json_document(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create a JSON document for testing
        json_document = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                data={
                    "original_key": "original_value"
                }
            )
        )

        # Create the update request
        request = create_request(
            method="POST",
            path=f"/json-document/{json_document.document_id}",
            headers={
                "Authorization": access_token
            },
            body={
                "data": {
                    "original_key": "updated_value",
                    "new_key": "new_value"
                }
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check we updated the document
        self.assertEqual(body["data"]["original_key"], "updated_value")
        self.assertEqual(body["data"]["new_key"], "new_value")

        # Clean up
        JSONDocument.delete_json_document(json_document.document_id)
        
    def test_delete_json_document(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create a JSON document for testing
        json_document = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                data={
                    "test_key": "test_value"
                }
            )
        )

        # Create the delete request
        request = create_request(
            method="DELETE",
            path=f"/json-document/{json_document.document_id}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Verify deletion was successful
        self.assertTrue(body["success"])
        
        # Verify the document no longer exists
        try:
            JSONDocument.get_json_document(json_document.document_id)
            self.fail("Document should have been deleted")
        except Exception as e:
            self.assertIn("404", str(e))
            
    def test_get_json_documents(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        
        # Create a few JSON documents for testing
        doc1 = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                data={"name": "Document 1"}
            )
        )
        
        doc2 = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                data={"name": "Document 2"}
            )
        )
        
        # Create the request
        request = create_request(
            method="GET",
            path="/json-documents",
            headers={
                "Authorization": access_token
            },
            query_string_parameters={
                "org_id": user.organizations[0]
            }
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check that the documents are returned
        self.assertIn("json_documents", body)
        
        # Extract document IDs from response
        response_doc_ids = [doc["document_id"] for doc in body["json_documents"]]
        
        # Verify our created documents are in the list
        self.assertIn(doc1.document_id, response_doc_ids)
        self.assertIn(doc2.document_id, response_doc_ids)

        # Clean up
        JSONDocument.delete_json_document(doc1.document_id)
        JSONDocument.delete_json_document(doc2.document_id)

    def test_public_json_document(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create a public JSON document for testing
        json_document = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                is_public=True,  # Set document as public
                data={
                    "test_key": "public_value",
                    "nested": {
                        "field1": "public_data",
                        "field2": 100
                    }
                }
            )
        )

        # Create the request WITHOUT authentication headers
        request = create_request(
            method="GET",
            path=f"/json-document/{json_document.document_id}"
            # No auth headers provided
        )

        # Call the lambda handler
        response = lambda_handler(request, None)

        # Check the response
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        # Check the response body
        self.assertEqual(body["document_id"], json_document.document_id)
        self.assertEqual(body["data"]["test_key"], "public_value")
        self.assertEqual(body["is_public"], True)
        self.assertEqual(body["data"]["nested"]["field2"], 100)

        # Try to access a non-public document without authentication
        private_document = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                is_public=False,  # Set document as private
                data={"private": "data"}
            )
        )

        # Create request for private document without auth
        private_request = create_request(
            method="GET",
            path=f"/json-document/{private_document.document_id}"
            # No auth headers provided
        )

        # Call the lambda handler
        private_response = lambda_handler(private_request, None)
        
        # Should get a 403 forbidden or 401 unauthorized
        self.assertIn(private_response["statusCode"], [401, 403])

        # Clean up
        JSONDocument.delete_json_document(json_document.document_id)
        JSONDocument.delete_json_document(private_document.document_id)


