"""
Model Gauntlet Tests

Pulls all models from the models table and runs each through a battery of
tests using AgentChat (sync), TokenStreamingAgentChat (async/streaming),
and llm_extract to validate that every configured model works correctly.
"""

import sys
import os
import unittest
import asyncio
from typing import Literal

from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from LLM.CreateLLM import create_llm
from LLM.AgentChat import AgentChat
from LLM.TokenStreamingAgentChat import TokenStreamingAgentChat
from LLM.AgentTool import AgentTool
from LLM.LLMExtract import llm_extract
from Models.LLMModel import get_all_models


# ─── Tool param models ───────────────────────────────────────────────

class get_weather(BaseModel):
    """Get the current weather for a city."""
    city: str

class get_time(BaseModel):
    """Get the current time."""
    pass

class SentimentResult(BaseModel):
    """The sentiment of a piece of text."""
    sentiment: Literal["positive", "negative", "neutral"]


# ─── Sync tool functions (for AgentChat) ─────────────────────────────

def get_weather_func(city: str) -> str:
    return f"Sunny and 25°C in {city}"

def get_time_func() -> str:
    return "The current time is 3:45 PM UTC"


# ─── Async tool functions (for TokenStreamingAgentChat) ──────────────

async def get_weather_func_async(city: str) -> str:
    return f"Sunny and 25°C in {city}"

async def get_time_func_async() -> str:
    return "The current time is 3:45 PM UTC"


# ─── Tool builders ───────────────────────────────────────────────────

def make_weather_tool(is_async=False):
    return AgentTool(
        tool_id="test_weather",
        params=get_weather,
        function=get_weather_func_async if is_async else get_weather_func,
    )

def make_time_tool(is_async=False):
    return AgentTool(
        tool_id="test_time",
        params=get_time,
        function=get_time_func_async if is_async else get_time_func,
    )


# ─── Helpers ─────────────────────────────────────────────────────────

async def consume_streaming_response(generator):
    """Fully consume an async generator returned by TokenStreamingAgentChat and return the concatenated content."""
    content = ""
    async for chunk in generator:
        content += chunk
    return content


def has_tool_message_containing(messages, text):
    """Check if any ToolMessage in the message list contains the given text."""
    for msg in messages:
        if isinstance(msg, ToolMessage) and text in msg.content:
            return True
    return False


class TestModelGauntlet(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.models = get_all_models()
        assert len(cls.models) > 0, "No models found in the models table — cannot run gauntlet tests"
        print(f"\n{'='*60}")
        print(f"Model Gauntlet: testing {len(cls.models)} model(s)")
        for m in cls.models:
            print(f"  - {m.model} ({m.model_provider})")
        print(f"{'='*60}\n")

    # ─── 1. Basic usage ──────────────────────────────────────────

    def test_basic_usage(self):
        """Add a human message and invoke, then do it again."""
        for model in self.models:
            with self.subTest(model=model.model):
                prompt = "You are a helpful assistant. Keep responses brief."

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=[],
                )
                response_1 = agent_chat.add_human_message_and_invoke("What is 2 + 2?")
                self.assertIsInstance(response_1, str)
                self.assertTrue(len(response_1) > 0, "First response should not be empty")

                response_2 = agent_chat.add_human_message_and_invoke("And what is 3 + 3?")
                self.assertIsInstance(response_2, str)
                self.assertTrue(len(response_2) > 0, "Second response should not be empty")
                self.assertGreaterEqual(len(agent_chat.messages), 4, "Should have at least 4 messages after two exchanges")

                # TokenStreamingAgentChat
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=[],
                )

                async def run_streaming():
                    gen_1 = await streaming_chat.add_human_message_and_invoke("What is 2 + 2?")
                    content_1 = await consume_streaming_response(gen_1)
                    self.assertTrue(len(content_1) > 0, "Streaming first response should not be empty")

                    gen_2 = await streaming_chat.add_human_message_and_invoke("And what is 3 + 3?")
                    content_2 = await consume_streaming_response(gen_2)
                    self.assertTrue(len(content_2) > 0, "Streaming second response should not be empty")
                    self.assertGreaterEqual(len(streaming_chat.messages), 4)

                asyncio.run(run_streaming())

    # ─── 2. Invoke before human message ──────────────────────────

    def test_invoke_before_human_message(self):
        """Invoke with no human message — agent speaks first. Skipped for Anthropic (requires at least one message)."""
        for model in self.models:
            with self.subTest(model=model.model):
                if model.model_provider == "anthropic":
                    continue

                prompt = "You are a helpful assistant. Greet the user proactively. Keep it brief."

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=[],
                )
                response = agent_chat.invoke(load_data_windows=False)
                self.assertIsInstance(response, str)
                self.assertTrue(len(response) > 0)

                # TokenStreamingAgentChat
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=[],
                )

                async def run_streaming():
                    gen = await streaming_chat.invoke(load_data_windows=False)
                    content = await consume_streaming_response(gen)
                    self.assertTrue(len(content) > 0)

                asyncio.run(run_streaming())

    # ─── 3. Tool with parameters ─────────────────────────────────

    def test_tool_with_parameters(self):
        """Agent calls a tool that takes a city parameter."""
        for model in self.models:
            with self.subTest(model=model.model):
                prompt = "You are a weather assistant. Use the get_weather tool to answer questions. Keep responses brief."

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=[],
                    tools=[make_weather_tool()],
                )
                response = agent_chat.add_human_message_and_invoke("What's the weather in Paris?")
                self.assertIsInstance(response, str)
                self.assertTrue(
                    has_tool_message_containing(agent_chat.messages, "Sunny") or
                    has_tool_message_containing(agent_chat.messages, "Paris"),
                    "Expected the weather tool to have been called with Paris"
                )

                # TokenStreamingAgentChat
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=[],
                    tools=[make_weather_tool(is_async=True)],
                )

                async def run_streaming():
                    gen = await streaming_chat.add_human_message_and_invoke("What's the weather in Paris?")
                    await consume_streaming_response(gen)
                    self.assertTrue(
                        has_tool_message_containing(streaming_chat.messages, "Sunny") or
                        has_tool_message_containing(streaming_chat.messages, "Paris"),
                    )

                asyncio.run(run_streaming())

    # ─── 4. Tool with no parameters ──────────────────────────────

    def test_tool_no_parameters(self):
        """Agent calls a tool that takes no parameters."""
        for model in self.models:
            with self.subTest(model=model.model):
                prompt = "You are a time assistant. Use the get_time tool to answer questions. Keep responses brief."

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=[],
                    tools=[make_time_tool()],
                )
                response = agent_chat.add_human_message_and_invoke("What time is it?")
                self.assertIsInstance(response, str)
                self.assertTrue(
                    has_tool_message_containing(agent_chat.messages, "3:45 PM"),
                    "Expected the time tool to have been called"
                )

                # TokenStreamingAgentChat
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=[],
                    tools=[make_time_tool(is_async=True)],
                )

                async def run_streaming():
                    gen = await streaming_chat.add_human_message_and_invoke("What time is it?")
                    await consume_streaming_response(gen)
                    self.assertTrue(
                        has_tool_message_containing(streaming_chat.messages, "3:45 PM"),
                    )

                asyncio.run(run_streaming())

    # ─── 5. Multiple tools ───────────────────────────────────────

    def test_multiple_tools(self):
        """Agent uses two different tools in a single conversation."""
        for model in self.models:
            with self.subTest(model=model.model):
                prompt = (
                    "You are a helpful assistant with access to weather and time tools. "
                    "Use both tools when asked. Keep responses brief."
                )

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=[],
                    tools=[make_weather_tool(), make_time_tool()],
                )
                response = agent_chat.add_human_message_and_invoke(
                    "What's the weather in Tokyo and what time is it?"
                )
                self.assertIsInstance(response, str)
                self.assertTrue(
                    has_tool_message_containing(agent_chat.messages, "Sunny"),
                    "Expected the weather tool to have been called"
                )
                self.assertTrue(
                    has_tool_message_containing(agent_chat.messages, "3:45 PM"),
                    "Expected the time tool to have been called"
                )

                # TokenStreamingAgentChat
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=[],
                    tools=[make_weather_tool(is_async=True), make_time_tool(is_async=True)],
                )

                async def run_streaming():
                    gen = await streaming_chat.add_human_message_and_invoke(
                        "What's the weather in Tokyo and what time is it?"
                    )
                    await consume_streaming_response(gen)
                    self.assertTrue(has_tool_message_containing(streaming_chat.messages, "Sunny"))
                    self.assertTrue(has_tool_message_containing(streaming_chat.messages, "3:45 PM"))

                asyncio.run(run_streaming())

    # ─── 6. Add AI message then invoke ───────────────────────────

    def test_set_ai_message_and_invoke(self):
        """Start with a pre-existing human + AI exchange, then continue the conversation."""
        for model in self.models:
            with self.subTest(model=model.model):
                prompt = "You are a helpful assistant. Keep responses brief."

                initial_messages = [
                    HumanMessage(content="Hi there"),
                    AIMessage(content="Hello! How can I help you today?"),
                ]

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=list(initial_messages),
                )
                response = agent_chat.add_human_message_and_invoke("What did I just say to you?")
                self.assertIsInstance(response, str)
                self.assertTrue(len(response) > 0)

                # TokenStreamingAgentChat
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=list(initial_messages),
                )

                async def run_streaming():
                    gen = await streaming_chat.add_human_message_and_invoke("What did I just say to you?")
                    content = await consume_streaming_response(gen)
                    self.assertTrue(len(content) > 0)

                asyncio.run(run_streaming())

    # ─── 7. Set new messages and invoke ──────────────────────────

    def test_set_new_messages_and_invoke(self):
        """Create a chat and invoke with a fresh set of messages."""
        for model in self.models:
            with self.subTest(model=model.model):
                prompt = "You are a helpful assistant. Keep responses brief."

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=[HumanMessage(content="Tell me a joke")],
                )
                response = agent_chat.invoke(load_data_windows=False)
                self.assertIsInstance(response, str)
                self.assertTrue(len(response) > 0)

                # TokenStreamingAgentChat
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=[HumanMessage(content="Tell me a joke")],
                )

                async def run_streaming():
                    gen = await streaming_chat.invoke(load_data_windows=False)
                    content = await consume_streaming_response(gen)
                    self.assertTrue(len(content) > 0)

                asyncio.run(run_streaming())

    # ─── 8. Foreign tool messages and invoke ─────────────────────

    def test_foreign_tool_messages_and_invoke(self):
        """Invoke with prior tool call/response messages from tools not bound to the agent."""
        for model in self.models:
            with self.subTest(model=model.model):
                prompt = "You are a helpful assistant. Keep responses brief."

                foreign_messages = [
                    HumanMessage(content="Look up user 42"),
                    AIMessage(
                        content="",
                        tool_calls=[{
                            "id": "call_foreign_123",
                            "name": "lookup_user",
                            "args": {"user_id": "42"}
                        }]
                    ),
                    ToolMessage(
                        tool_call_id="call_foreign_123",
                        content='{"name": "Alice", "email": "alice@example.com"}'
                    ),
                    HumanMessage(content="Great, what was that user's name?"),
                ]

                # AgentChat (no tools bound)
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=list(foreign_messages),
                )
                response = agent_chat.invoke(load_data_windows=False)
                self.assertIsInstance(response, str)
                self.assertTrue(len(response) > 0)

                # TokenStreamingAgentChat (no tools bound)
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=list(foreign_messages),
                )

                async def run_streaming():
                    gen = await streaming_chat.invoke(load_data_windows=False)
                    content = await consume_streaming_response(gen)
                    self.assertTrue(len(content) > 0)

                asyncio.run(run_streaming())

    # ─── 9. Token tracking via on_response callback ──────────────

    def test_token_tracking_callback(self):
        """Verify that on_response receives usage_metadata with token counts."""
        for model in self.models:
            with self.subTest(model=model.model):
                prompt = "You are a helpful assistant. Keep responses brief."

                captured_responses = []

                def on_response(response):
                    captured_responses.append(response)

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=[],
                    on_response=on_response,
                )
                agent_chat.add_human_message_and_invoke("Say hello")
                self.assertGreater(len(captured_responses), 0, "on_response should have been called")

                last_response = captured_responses[-1]
                usage = getattr(last_response, 'usage_metadata', None)
                self.assertIsNotNone(usage, f"usage_metadata missing on response for {model.model}")

                input_tokens = usage.get('input_tokens', 0) if isinstance(usage, dict) else getattr(usage, 'input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0) if isinstance(usage, dict) else getattr(usage, 'output_tokens', 0)
                self.assertGreater(input_tokens, 0, "input_tokens should be > 0")
                self.assertGreater(output_tokens, 0, "output_tokens should be > 0")

                # TokenStreamingAgentChat
                streaming_responses = []

                def on_streaming_response(response):
                    streaming_responses.append(response)

                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=[],
                    on_response=on_streaming_response,
                )

                async def run_streaming():
                    gen = await streaming_chat.add_human_message_and_invoke("Say hello")
                    await consume_streaming_response(gen)

                asyncio.run(run_streaming())

                self.assertGreater(len(streaming_responses), 0, "Streaming on_response should have been called")
                streaming_usage = getattr(streaming_responses[-1], 'usage_metadata', None)
                self.assertIsNotNone(streaming_usage, f"Streaming usage_metadata missing for {model.model}")

    # ─── 10. llm_extract ─────────────────────────────────────────

    def test_llm_extract(self):
        """Verify llm_extract returns a valid structured result for each model."""
        for model in self.models:
            with self.subTest(model=model.model):
                llm = create_llm(model.model)
                result = llm_extract(SentimentResult, "I absolutely love sunshine and warm weather!", llm)
                self.assertIn("sentiment", result)
                self.assertIn(result["sentiment"], ["positive", "negative", "neutral"])

    # ─── 11. Multi-turn tool loop ────────────────────────────────

    def test_multi_turn_tool_loop(self):
        """Agent calls the same tool multiple times across recursive invocations."""
        for model in self.models:
            with self.subTest(model=model.model):
                prompt = (
                    "You are a weather assistant. You have a get_weather tool that checks one city at a time. "
                    "When asked about multiple cities, call the tool once for each city. Keep responses brief."
                )

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=[],
                    tools=[make_weather_tool()],
                )
                response = agent_chat.add_human_message_and_invoke(
                    "What's the weather in Paris and London?"
                )
                self.assertIsInstance(response, str)

                weather_tool_calls = [
                    msg for msg in agent_chat.messages
                    if isinstance(msg, ToolMessage) and "Sunny" in msg.content
                ]
                self.assertGreaterEqual(
                    len(weather_tool_calls), 2,
                    f"Expected at least 2 weather tool calls, got {len(weather_tool_calls)}"
                )

                # TokenStreamingAgentChat
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=[],
                    tools=[make_weather_tool(is_async=True)],
                )

                async def run_streaming():
                    gen = await streaming_chat.add_human_message_and_invoke(
                        "What's the weather in Paris and London?"
                    )
                    await consume_streaming_response(gen)
                    weather_calls = [
                        msg for msg in streaming_chat.messages
                        if isinstance(msg, ToolMessage) and "Sunny" in msg.content
                    ]
                    self.assertGreaterEqual(len(weather_calls), 2)

                asyncio.run(run_streaming())

    # ─── 12. Multiple system messages mid-conversation ───────────

    def test_multiple_system_messages(self):
        """Inject a system message mid-conversation (like AddAIMessageHandler does) and invoke. Skipped for Anthropic (no non-consecutive system messages)."""
        for model in self.models:
            with self.subTest(model=model.model):
                if model.model_provider == "anthropic":
                    continue

                prompt = "You are a helpful assistant. Keep responses brief."

                mid_conversation_messages = [
                    HumanMessage(content="Hi"),
                    AIMessage(content="Hello! How can I help?"),
                    SystemMessage(content="From now on, respond only in French."),
                    HumanMessage(content="What color is the sky?"),
                ]

                # AgentChat
                agent_chat = AgentChat(
                    llm=create_llm(model.model),
                    prompt=prompt,
                    messages=list(mid_conversation_messages),
                )
                response = agent_chat.invoke(load_data_windows=False)
                self.assertIsInstance(response, str)
                self.assertTrue(len(response) > 0, "Should respond after mid-conversation system message")

                # TokenStreamingAgentChat
                streaming_chat = TokenStreamingAgentChat(
                    llm=create_llm(model.model, for_streaming=True),
                    prompt=prompt,
                    messages=list(mid_conversation_messages),
                )

                async def run_streaming():
                    gen = await streaming_chat.invoke(load_data_windows=False)
                    content = await consume_streaming_response(gen)
                    self.assertTrue(len(content) > 0)

                asyncio.run(run_streaming())


if __name__ == "__main__":
    unittest.main()
