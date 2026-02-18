import json
import unittest
import sys
sys.path.append("../")
from tests.config import access_token
from src.lambda_function import lambda_handler
from tests.helper_funcs import create_request
from src.AWS import Cognito
from src.AWS.Lambda import LambdaEvent
from src.Models import Job
from src.LLM.InteliSort import inteli_sort
from src.RequestHandlers.InteliSort.RunInteliSortHandler import inteli_sort_handler


# ── Test leads: intentionally unordered, clearly cold to hot ──
LEADS = [
    "Hi, I saw your ad. Can you send me some general information about your services?",
    "We urgently need a solution like yours. Can we get a contract drafted and sign this week?",
    "Please remove me from your mailing list. I am not interested.",
    "This looks promising! What's the pricing? We have budget allocated for Q1.",
    "I'm just browsing, not sure if this is relevant to us.",
    "We've evaluated three vendors and yours is our top pick. Let's schedule a final call to close the deal.",
    "Interesting concept. I'll bring it up at our next team meeting and get back to you.",
    "Not the right time for us. Maybe revisit in a year or so.",
]

PROMPT = (
    "You are evaluating two sales leads based on buying intent. "
    "Which lead is hotter and more likely to convert into a paying customer?\n\n"
    "Lead A: ARG_ITEM_A\n\n"
    "Lead B: ARG_ITEM_B\n\n"
    "Choose the lead that demonstrates stronger buying intent."
)


class TestInteliSortAlgorithm(unittest.TestCase):
    """Tests the inteli_sort algorithm with a deterministic mock compare function."""

    def test_sort_numbers(self):
        """Sort items by numeric value using a simple comparator."""
        items = [
            {"id": "a", "value": 3},
            {"id": "b", "value": 1},
            {"id": "c", "value": 5},
            {"id": "d", "value": 2},
            {"id": "e", "value": 4},
        ]

        def compare(a, b):
            return a if a["value"] > b["value"] else b

        results = inteli_sort(items, compare, n=3, log=print)

        result_ids = [r["id"] for r in results]
        self.assertEqual(result_ids, ["c", "e", "a"])

    def test_sort_all_items(self):
        """Sort all items (n == len(items))."""
        items = [
            {"id": "x", "value": 10},
            {"id": "y", "value": 30},
            {"id": "z", "value": 20},
        ]

        def compare(a, b):
            return a if a["value"] > b["value"] else b

        results = inteli_sort(items, compare, n=3, log=print)

        result_ids = [r["id"] for r in results]
        self.assertEqual(result_ids, ["y", "z", "x"])

    def test_sort_single_winner(self):
        """Select only the top 1 item."""
        items = [
            {"id": "1", "value": 5},
            {"id": "2", "value": 9},
            {"id": "3", "value": 1},
            {"id": "4", "value": 7},
        ]

        def compare(a, b):
            return a if a["value"] > b["value"] else b

        results = inteli_sort(items, compare, n=1, log=print)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "2")

    def test_odd_number_of_items(self):
        """Verify bye handling with an odd number of items."""
        items = [
            {"id": "a", "value": 1},
            {"id": "b", "value": 3},
            {"id": "c", "value": 2},
        ]

        def compare(a, b):
            return a if a["value"] > b["value"] else b

        results = inteli_sort(items, compare, n=2, log=print)

        result_ids = [r["id"] for r in results]
        self.assertEqual(result_ids, ["b", "c"])


class TestInteliSortHandler(unittest.TestCase):
    """Integration test: calls the handler directly with real LLM comparisons."""

    def test_sort_leads_with_llm(self):
        """Sort sales leads by buying intent using the LLM."""

        # Create a Job in DynamoDB (simulating what lambda_function.py Phase 1 does)
        cognito_user = Cognito.get_user_from_cognito(access_token)
        job = Job.create_job(owner_id=cognito_user.sub, data={})

        n = 3

        # Build a LambdaEvent matching what lambda_function.py would construct
        lambda_event = LambdaEvent(
            path="/inteli-sort",
            httpMethod="POST",
            headers={"Authorization": access_token},
            body=json.dumps({
                "items": LEADS,
                "prompt": PROMPT,
                "n": n,
            }),
            runJobId=job.job_id,
        )

        # Call the handler directly (Phase 2)
        result_job = inteli_sort_handler(lambda_event=lambda_event, user=cognito_user)

        # Assertions
        self.assertEqual(result_job.status, Job.JobStatus.completed)
        self.assertEqual(len(result_job.data["results"]), n)
        self.assertGreater(len(result_job.data["logs"]), 0)

        # Print results for manual inspection
        print("\n── InteliSort Results ──")
        for i, item in enumerate(result_job.data["results"]):
            print(f"  #{i + 1}: {item['value']}")

        # The top results should be the hot leads (buying intent)
        # Leads at index 1 and 5 are clearly the hottest:
        #   1: "We urgently need a solution..."
        #   5: "We've evaluated three vendors..."
        top_values = [item["value"] for item in result_job.data["results"]]
        self.assertIn(LEADS[1], top_values, "Hottest lead should be in top results")
        self.assertIn(LEADS[5], top_values, "Second hottest lead should be in top results")

        # Clean up
        Job.delete_job(result_job.job_id)

    def test_sort_leads_with_id_value_objects(self):
        """Sort leads passed as {id, value} objects instead of plain strings."""

        cognito_user = Cognito.get_user_from_cognito(access_token)
        job = Job.create_job(owner_id=cognito_user.sub, data={})

        items_with_ids = [
            {"id": "lead-cold", "value": "Not interested. Please don't contact me again."},
            {"id": "lead-warm", "value": "Looks interesting. What are the next steps to get started?"},
            {"id": "lead-hot", "value": "We want to purchase immediately. Send us the invoice."},
            {"id": "lead-lukewarm", "value": "I'll think about it and maybe follow up later."},
        ]

        lambda_event = LambdaEvent(
            path="/inteli-sort",
            httpMethod="POST",
            headers={"Authorization": access_token},
            body=json.dumps({
                "items": items_with_ids,
                "prompt": PROMPT,
                "n": 2,
            }),
            runJobId=job.job_id,
        )

        result_job = inteli_sort_handler(lambda_event=lambda_event, user=cognito_user)

        self.assertEqual(result_job.status, Job.JobStatus.completed)
        self.assertEqual(len(result_job.data["results"]), 2)

        # Print results
        print("\n── InteliSort Results (id/value objects) ──")
        for i, item in enumerate(result_job.data["results"]):
            print(f"  #{i + 1} [{item['id']}]: {item['value']}")

        # The top 2 should be hot and warm
        top_ids = [item["id"] for item in result_job.data["results"]]
        self.assertIn("lead-hot", top_ids, "Hottest lead should be in top results")
        self.assertIn("lead-warm", top_ids, "Warm lead should be in top 2")

        # Clean up
        Job.delete_job(result_job.job_id)


class TestInteliSortEndpoint(unittest.TestCase):
    """Tests the /inteli-sort endpoint through lambda_handler (Phase 1 only)."""

    def test_endpoint_returns_job(self):
        """POST /inteli-sort should return 202 with a Job."""

        request = create_request(
            method="POST",
            path="/inteli-sort",
            headers={"Authorization": access_token},
            body={
                "items": ["Lead A", "Lead B", "Lead C"],
                "prompt": PROMPT,
                "n": 2,
            },
        )

        response = lambda_handler(request, None)

        self.assertEqual(response["statusCode"], 202)

        body = json.loads(response["body"])
        self.assertIn("job_id", body)
        self.assertEqual(body["status"], "queued")

        print(f"\n── Endpoint returned Job: {body['job_id']} ──")

        # Clean up
        Job.delete_job(body["job_id"])

    def test_endpoint_requires_auth(self):
        """POST /inteli-sort without auth should return 401."""

        request = create_request(
            method="POST",
            path="/inteli-sort",
            headers={},
            body={
                "items": ["Lead A", "Lead B"],
                "prompt": PROMPT,
                "n": 1,
            },
        )

        response = lambda_handler(request, None)

        self.assertEqual(response["statusCode"], 401)
