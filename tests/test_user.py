import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token, user_email
from src.lambda_function import lambda_handler

class TestUser(unittest.TestCase):
    def test_get_user(self):
        request = create_request(
            method="GET",
            path="/user",
            headers={
                "Authorization": access_token
            }
        )
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(json.loads(result["body"])["email"], user_email)

    def test_get_user_with_bad_token(self):
        request = create_request(
            method="GET",
            path="/user",
            headers={
                "Authorization": "bad_token"
            }
        )
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 401)


    # def test_delete_user(self):
    #     request = create_request(
    #         method="DELETE",
    #         path="/user",
    #         headers={
    #             "Authorization": access_token
    #         }
    #     )
    #     result = lambda_handler(request, None)
    #     self.assertEqual(result["statusCode"], 200) # Deletion successful

    #     request = create_request(
    #         method="GET",
    #         path="/user",
    #         headers={
    #             "Authorization": access_token
    #         }
    #     )
    #     result = lambda_handler(request, None)
    #     self.assertEqual(result["statusCode"], 401) # Unauthorized after delete
        