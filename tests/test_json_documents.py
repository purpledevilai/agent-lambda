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


    def test_set_get_add_delete_and_shape(self):
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        doc = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                data={"profile": {"first": "keanu"}, "people": []}
            )
        )

        # Set a value
        req = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/set",
            headers={"Authorization": access_token},
            body={"path": "profile.last", "value": "reeves", "type": "string"}
        )
        res = lambda_handler(req, None)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        print("Set Response:", json.dumps(body, indent=2))
        self.assertEqual(body["data"]["profile"]["last"], "reeves")

        # Add list item
        req = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/add",
            headers={"Authorization": access_token},
            body={"path": "people", "value": "Alice", "type": "string"}
        )
        res = lambda_handler(req, None)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        print("Add Response:", json.dumps(body, indent=2))
        self.assertIn("Alice", body["data"]["people"])

        # Get value
        req = create_request(
            method="GET",
            path=f"/json-document/{doc.document_id}/value",
            headers={"Authorization": access_token},
            query_string_parameters={"path": "profile.last"}
        )
        res = lambda_handler(req, None)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        print("Get Value Response:", json.dumps(body, indent=2))
        self.assertEqual(body["value"], "reeves")

        # Delete value
        req = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/delete",
            headers={"Authorization": access_token},
            body={"path": "profile.last"}
        )
        res = lambda_handler(req, None)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        print("Delete Response:", json.dumps(body, indent=2))
        self.assertNotIn("last", body["data"]["profile"])

        # Get shape
        req = create_request(
            method="GET",
            path=f"/json-document/{doc.document_id}/shape",
            headers={"Authorization": access_token}
        )
        res = lambda_handler(req, None)
        body = json.loads(res["body"])
        self.assertEqual(res["statusCode"], 200)
        print("Shape Response:", json.dumps(body, indent=2))
        self.assertIn("string", body["schema"]["people"])
        self.assertEqual(body["schema"]["profile"], {"first": "string"})

        # Add a person object to people
        req = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/add",
            headers={"Authorization": access_token},
            body={"path": "people", "value": json.dumps({"name": "Bob", "age": 30}), "type": "json"}
        )
        res = lambda_handler(req, None)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        print("Add Object Response:", json.dumps(body, indent=2))
        self.assertIn({"name": "Bob", "age": 30}, body["data"]["people"])

        # Set a pets list
        req = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/set",
            headers={"Authorization": access_token},
            body={"path": "pets", "value": json.dumps([{"name": "Athena", "type_code": 2}, {"name": "Failt", "type_code": 2}]), "type": "json"}
        )
        res = lambda_handler(req, None)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        print("Set Pets Response:", json.dumps(body, indent=2))

        # Get the shape again
        req = create_request(
            method="GET",
            path=f"/json-document/{doc.document_id}/shape",
            headers={"Authorization": access_token}
        )
        res = lambda_handler(req, None)
        body = json.loads(res["body"])
        self.assertEqual(res["statusCode"], 200)
        print("Updated Shape Response:", json.dumps(body, indent=2))
        self.assertEqual(body["schema"]["pets"], [{"name": "string", "type_code": "number"}])

        # Add a variation to pets
        req = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/add",
            headers={"Authorization": access_token},
            body={"path": "pets", "value": json.dumps({"name": "Luna", "type_code": 2, "age": 3}), "type": "json"}
        )
        res = lambda_handler(req, None)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        print("Add Variation Response:", json.dumps(body, indent=2))
        self.assertIn({"name": "Luna", "type_code": 2, "age": 3}, body["data"]["pets"])

        # Get the shape again
        req = create_request(
            method="GET",
            path=f"/json-document/{doc.document_id}/shape",
            headers={"Authorization": access_token}
        )
        res = lambda_handler(req, None)
        body = json.loads(res["body"])
        self.assertEqual(res["statusCode"], 200)
        print("Updated Shape Response:", json.dumps(body, indent=2))
        self.assertEqual(body["schema"]["pets"], [{"name": "string", "type_code": "number", "age": "optional number"}])

        JSONDocument.delete_json_document(doc.document_id)

    def test_public_document_operations(self):
        # Set up - Create a public document with authentication
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        # Create a public JSON document for testing
        doc = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                is_public=True,  # Set document as public
                data={
                    "profile": {"first": "john"},
                    "tags": ["personal"],
                    "items": []
                }
            )
        )

        # 1. Set a value without authentication
        set_request = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/set",
            # No auth headers
            body={"path": "profile.last", "value": "doe", "type": "string"}
        )
        set_response = lambda_handler(set_request, None)
        self.assertEqual(set_response["statusCode"], 200)
        set_body = json.loads(set_response["body"])
        print("Public Set Response:", json.dumps(set_body, indent=2))
        
        # Verify the value was set
        self.assertEqual(set_body["data"]["profile"]["last"], "doe")
        
        # 2. Add an item to a list without authentication
        add_request = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/add",
            # No auth headers
            body={"path": "tags", "value": "public", "type": "string"}
        )
        add_response = lambda_handler(add_request, None)
        self.assertEqual(add_response["statusCode"], 200)
        add_body = json.loads(add_response["body"])
        print("Public Add Response:", json.dumps(add_body, indent=2))
        
        # Verify item was added to the list
        self.assertIn("public", add_body["data"]["tags"])
        
        # 3. Add a complex object to a list without authentication
        add_obj_request = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/add",
            # No auth headers
            body={"path": "items", "value": json.dumps({"name": "Item 1", "quantity": 5}), "type": "json"}
        )
        add_obj_response = lambda_handler(add_obj_request, None)
        self.assertEqual(add_obj_response["statusCode"], 200)
        add_obj_body = json.loads(add_obj_response["body"])
        print("Public Add Object Response:", json.dumps(add_obj_body, indent=2))
        
        # Verify complex object was added
        self.assertEqual(add_obj_body["data"]["items"][0]["name"], "Item 1")
        self.assertEqual(add_obj_body["data"]["items"][0]["quantity"], 5)
        
        # 4. Delete a value without authentication
        delete_request = create_request(
            method="POST",
            path=f"/json-document/{doc.document_id}/delete",
            # No auth headers
            body={"path": "profile.first"}
        )
        delete_response = lambda_handler(delete_request, None)
        self.assertEqual(delete_response["statusCode"], 200)
        delete_body = json.loads(delete_response["body"])
        print("Public Delete Response:", json.dumps(delete_body, indent=2))
        
        # Verify the value was deleted
        self.assertNotIn("first", delete_body["data"]["profile"])
        
        # 5. Verify a private document rejects operations without auth
        private_doc = JSONDocument.create_json_document(
            JSONDocument.CreateJSONDocumentParams(
                org_id=user.organizations[0],
                is_public=False,  # Set document as private
                data={"private": "data"}
            )
        )
        
        private_request = create_request(
            method="POST",
            path=f"/json-document/{private_doc.document_id}/set",
            # No auth headers
            body={"path": "new_field", "value": "test", "type": "string"}
        )
        private_response = lambda_handler(private_request, None)
        
        # Should get a 403 forbidden or 401 unauthorized
        self.assertIn(private_response["statusCode"], [401, 403])
        
        # Clean up
        JSONDocument.delete_json_document(doc.document_id)
        JSONDocument.delete_json_document(private_doc.document_id)

