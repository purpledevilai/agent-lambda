import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
# Imports for test

class TestScrapePage(unittest.TestCase):


    def test_scrape_page(self):

        link = "https://realboss.ai/"

        # Create request
        request = create_request(
            method="GET",
            path=f"/scrape-page/{link}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check content not empty
        self.assertTrue(res_body["page_content"])