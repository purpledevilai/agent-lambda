import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token, agent_id_outside_of_org
from src.lambda_function import lambda_handler
# Import for test
from src.AWS import Cognito
from src.Models import Job, User

class TestJob(unittest.TestCase):

    def test_get_job(self):

        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        job: Job.Job = Job.create_job(
            owner_id=user.user_id,
        )
        
        # Create request
        request = create_request(
            method="GET",
            path=f"/job/{job.job_id}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        print(res_body)

        # Check for job
        self.assertTrue("status" in res_body)
        
        # Check if job id is in job list
        self.assertEqual(res_body["owner_id"], user.user_id)

        # Clean up
        Job.delete_job(job.job_id)