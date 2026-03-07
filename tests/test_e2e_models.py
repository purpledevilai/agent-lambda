"""
End-to-End Model Smoke Tests

For each model in the models table, creates an agent with that model,
hits the /chat endpoint, verifies tool calling via get_time, and
confirms context retrieval works.
"""

import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
from src.AWS import Cognito
from src.Models import Context, Agent, User
from src.Models.LLMModel import get_all_models


class TestE2EModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.models = get_all_models()
        assert len(cls.models) > 0, "No models found in the models table"

        cognito_user = Cognito.get_user_from_cognito(access_token)
        cls.user = User.get_user(cognito_user.sub)

        cls.agent = Agent.create_agent(
            agent_name="e2e-smoke-test-agent",
            agent_description="Agent for e2e model smoke tests",
            prompt="You are a helpful assistant. When asked for the time, use the get_time tool with the timezone provided. Keep responses brief.",
            org_id=cls.user.organizations[0],
            is_public=False,
            agent_speaks_first=False,
            tools=["get_time"],
        )

        cls.contexts_to_cleanup = []

        print(f"\n{'='*60}")
        print(f"E2E Smoke Test: testing {len(cls.models)} model(s)")
        for m in cls.models:
            print(f"  - {m.model} ({m.model_provider})")
        print(f"{'='*60}\n")

    @classmethod
    def tearDownClass(cls):
        for context_id in cls.contexts_to_cleanup:
            try:
                Context.delete_context(context_id)
            except Exception:
                pass
        try:
            Agent.delete_agent(cls.agent.agent_id)
        except Exception:
            pass

    def _update_agent_model(self, model_id):
        request = create_request(
            method="POST",
            path=f"/agent/{self.agent.agent_id}",
            body={"model_id": model_id},
            headers={"Authorization": access_token},
        )
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200, f"Failed to update agent model to {model_id}: {result.get('body')}")

    def _create_context(self):
        request = create_request(
            method="POST",
            path="/context",
            body={"agent_id": self.agent.agent_id},
            headers={"Authorization": access_token},
        )
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200, f"Failed to create context: {result.get('body')}")
        body = json.loads(result["body"])
        self.contexts_to_cleanup.append(body["context_id"])
        return body["context_id"]

    def _chat(self, context_id, message):
        request = create_request(
            method="POST",
            path="/chat",
            body={"context_id": context_id, "message": message},
            headers={"Authorization": access_token},
        )
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200, f"Chat failed: {result.get('body')}")
        return json.loads(result["body"])

    def _get_context(self, context_id, with_tool_calls=False):
        qsp = {"with_tool_calls": "true"} if with_tool_calls else {}
        request = create_request(
            method="GET",
            path=f"/context/{context_id}",
            headers={"Authorization": access_token},
            query_string_parameters=qsp,
        )
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200, f"Get context failed: {result.get('body')}")
        return json.loads(result["body"])

    def test_model_smoke(self):
        """For each model: chat, verify response, call get_time tool, verify tool usage, get context."""
        for model in self.models:
            with self.subTest(model=model.model):
                print(f"\n--- Testing {model.model} ({model.model_provider}) ---")

                # Update agent to use this model
                self._update_agent_model(model.model)

                # Create a fresh context
                context_id = self._create_context()

                # Step 1: Send a greeting and verify response
                chat_response_1 = self._chat(context_id, "Hey there")
                self.assertIn("response", chat_response_1)
                self.assertIsNotNone(chat_response_1["response"])
                self.assertGreater(len(chat_response_1["response"]), 0, "Response should not be empty")
                print(f"  Chat 1 response: {chat_response_1['response'][:100]}...")

                # Step 2: Verify context has at least 2 messages (human + ai)
                ctx_1 = self._get_context(context_id)
                self.assertGreaterEqual(
                    len(ctx_1["messages"]), 2,
                    f"Expected at least 2 messages after first chat, got {len(ctx_1['messages'])}"
                )

                # Step 3: Ask agent to call get_time tool with Sydney timezone
                chat_response_2 = self._chat(context_id, "Can you call the get_time tool with the Australia/Sydney timezone?")
                self.assertIn("response", chat_response_2)
                self.assertIsNotNone(chat_response_2["response"])
                print(f"  Chat 2 response: {chat_response_2['response'][:100]}...")

                # Step 4: Verify tool was called by checking generated_messages
                generated = chat_response_2.get("generated_messages", [])
                tool_call_msgs = [m for m in generated if m.get("type") == "tool_call"]
                tool_response_msgs = [m for m in generated if m.get("type") == "tool_response"]

                self.assertGreater(
                    len(tool_call_msgs), 0,
                    f"Expected at least one tool_call in generated_messages for {model.model}"
                )
                get_time_calls = [tc for tc in tool_call_msgs if tc.get("tool_name") == "get_time"]
                self.assertGreater(
                    len(get_time_calls), 0,
                    f"Expected get_time tool call for {model.model}"
                )
                self.assertGreater(
                    len(tool_response_msgs), 0,
                    f"Expected at least one tool_response in generated_messages for {model.model}"
                )

                # Step 5: Get context with tool calls and verify structure
                ctx_2 = self._get_context(context_id, with_tool_calls=True)
                self.assertGreater(
                    len(ctx_2["messages"]), len(ctx_1["messages"]),
                    "Context should have more messages after tool-calling chat"
                )

                # Verify we have an AI message with tool calls in the raw context
                raw_context = Context.get_context(context_id)
                ai_with_tool_calls = [
                    m for m in raw_context.messages
                    if m.get("type") == "ai" and m.get("tool_calls") and len(m["tool_calls"]) > 0
                ]
                self.assertGreater(
                    len(ai_with_tool_calls), 0,
                    f"Expected an AI message with tool_calls in context for {model.model}"
                )
                tool_msg = [m for m in raw_context.messages if m.get("type") == "tool"]
                self.assertGreater(
                    len(tool_msg), 0,
                    f"Expected a tool response message in context for {model.model}"
                )

                # Step 6: Final GET context to ensure it loads cleanly
                ctx_final = self._get_context(context_id)
                self.assertIn("context_id", ctx_final)
                self.assertEqual(ctx_final["context_id"], context_id)

                print(f"  PASSED: {model.model}")


if __name__ == "__main__":
    unittest.main()
