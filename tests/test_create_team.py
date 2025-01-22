import json
import time
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token, cleaningly_page_data
from src.lambda_function import lambda_handler
# Import for test
from src.Models import Job, Agent

class TestCreateTeam(unittest.TestCase):

    def test_create_team(self):
        
        # Create request
        request = create_request(
            method="POST",
            path=f"/create-team",
            headers={
                "Authorization": access_token
            },
            body={
                "business_name": "cleaningly",
                "business_description": "business that cleans",
                "link_data": [
                    {
                        "link": "https://www.cleaningly.com.au/",
                        "data": cleaningly_page_data
                    }
                ],
                "selected_members": [
                    "customer-support",
                    "digital-marketing"
                ]
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # parse result
        result = json.loads(result["body"])

        # Check job_id in result
        self.assertTrue("job_id" in result)

        # poll job status until it's completed
        while True:
            print("Polling job status...")
            job = Job.get_job(result["job_id"])
            if job.status == Job.JobStatus.completed or job.status == Job.JobStatus.error:
                break
            # sleep for 2 seconds
            time.sleep(2)
        
        self.assertEqual(job.status, Job.JobStatus.completed)
        
        # Clean up
        job = Job.get_job(result["job_id"])
        for agent_template_id in job.data.keys():
            Agent.delete_agent(job.data[agent_template_id]["agent_id"])
        Job.delete_job(result["job_id"])

