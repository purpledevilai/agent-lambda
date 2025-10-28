import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token, agent_id_outside_of_org
from src.lambda_function import lambda_handler
# Import for test
from src.Models import Context, Agent, User, Tool
from src.AWS import Cognito
from src.LLM.AgentChat import AgentChat
from src.LLM.CreateLLM import create_llm
from src.LLM.BaseMessagesConverter import base_messages_to_dict_messages, dict_messages_to_base_messages


class TestContext(unittest.TestCase):

    def test_create_context(self):

        # Create org data
        agent_id = "aj"
        create_context_body = {
            "agent_id": agent_id
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_id"], agent_id)

        # Clean up
        Context.delete_context(res_body["context_id"])

    def test_create_public_context(self):

        # Create org data
        public_agent_id = "aj-public"
        create_context_body = {
            "agent_id": public_agent_id,
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_id"], public_agent_id)

        # Clean up
        Context.delete_context(res_body["context_id"])

    def test_create_context_for_non_public_agent(self):

        # Create org data
        non_public_agent_id = "aj"
        create_context_body = {
            "agent_id": non_public_agent_id
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 403)

    def test_create_context_for_an_outside_agent(self):

        # Create org data
        create_context_body = {
            "agent_id": agent_id_outside_of_org
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)
        print(result)

        # Check the response
        self.assertEqual(result["statusCode"], 403)

        

    def test_get_context(self):

        cognito_user = Cognito.get_user_from_cognito(access_token)
        context = Context.create_context("aj", cognito_user.sub)

        # Create request
        request = create_request(
            method="GET",
            path=f"/context/{context.context_id}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)
        
        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_id"], "aj")

        # Clean up
        Context.delete_context(context.context_id)

    def test_get_public_context(self):

        context: Context.Context = Context.create_context("aj-public", None)

        # Create request
        request = create_request(
            method="GET",
            path=f"/context/{context.context_id}"
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        # Check for name
        self.assertEqual(res_body["agent_id"], "aj-public")

        # Clean up
        Context.delete_context(context.context_id)

    def test_delete_context(self):

        cognito_user = Cognito.get_user_from_cognito(access_token)
        context = Context.create_context("aj", cognito_user.sub)

        # Create request
        request = create_request(
            method="DELETE",
            path=f"/context/{context.context_id}",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        self.assertEqual(res_body["success"], True)

    def test_get_context_history(self):

        cognito_user = Cognito.get_user_from_cognito(access_token)
        context = Context.create_context("aj", cognito_user.sub)

        # Create request
        request = create_request(
            method="GET",
            path="/context-history",
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])

        print("Context History Length: ", len(res_body["contexts"]))
        print("Last Context: ", res_body["contexts"][0])
        self.assertGreaterEqual(len(res_body["contexts"]), 1)

        # Clean up
        Context.delete_context(context.context_id)

    def test_create_context_with_prompt_args(self):

        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent("aj", "agent with prompt args", "Say hello to {name}", user.organizations[0], False, True)

        create_context_body = {
            "agent_id": agent.agent_id,
            "prompt_args": {
                "name": "Alice"
            }
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        res_body = json.loads(result["body"])

        # Check for name in the first message
        # Removing because message is streamed now
        #self.assertTrue("Alice" in res_body["messages"][0]["message"])

        # Clean up
        Context.delete_context(res_body["context_id"])
        Agent.delete_agent(agent.agent_id)

    def test_create_context_with_prompt_args_and_agent_speaks_first_with_no_params(self):

        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent("aj", "agent with prompt args", "Say hello to {name}", user.organizations[0], False, True)

        create_context_body = {
            "agent_id": agent.agent_id,
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=create_context_body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # Clean up
        Agent.delete_agent(agent.agent_id)
        Context.delete_context(json.loads(result["body"])["context_id"])


    def test_create_context_with_agent_that_has_tools_and_speaks_first(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            agent_name="test-agent",
            agent_description="test agent",
            prompt="Hello",
            org_id=user.organizations[0],
            agent_speaks_first=True,
            is_public=False,
            tools=["pass_event"]
        )
        body = {
            "agent_id": agent.agent_id
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # Clean up 
        res_body = json.loads(result["body"])
        Context.delete_context(res_body["context_id"])
        Agent.delete_agent(agent.agent_id)

    def test_create_context_with_agent_params_and_json_in_the_params(self): 

        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        prompt = "Describe what the following code does \n{code}"
        agent = Agent.create_agent(
            agent_name="test-agent",
            agent_description="test agent",
            prompt=prompt,
            org_id=user.organizations[0],
            agent_speaks_first=True,
            is_public=False
        )

        # body
        body = {
            "agent_id": agent.agent_id,
            "prompt_args": {
                "code": """
const sayHello(name: string) {
    print(`Hello, ${name}`)
}
"""
            }
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)

        # Clean up 
        res_body = json.loads(result["body"])
        Context.delete_context(res_body["context_id"])
        Agent.delete_agent(agent.agent_id)

    def get_context_with_tool_messages(self):
        context_with_tool_messages = "6dc15c64-223c-48f8-9e7f-8dea288a9887"

        # Create the request
        request = create_request(
            method="GET",
            path=f"/context/{context_with_tool_messages}",
            query_string_parameters={
                "with_tool_calls": True
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Get the body
        res_body = json.loads(result["body"])

        # Print result
        print(json.dumps(res_body, indent=4))

    def test_create_context_with_initialization_tool(self):
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        tool = Tool.create_tool(
            org_id=user.organizations[0],
            name="init_tool",
            description="initialize context",
            code="def init_tool():\n  return 'initialized'"
        )

        agent = Agent.create_agent(
            agent_name="init-agent",
            agent_description="agent with init tool",
            prompt="hello",
            org_id=user.organizations[0],
            is_public=False,
            agent_speaks_first=False,
            initialize_tool_id=tool.tool_id
        )

        context = Context.create_context(agent.agent_id, cognito_user.sub)

        self.assertTrue(len(context.messages) >= 2)
        self.assertEqual(context.messages[0]["type"], "ai")
        self.assertEqual(context.messages[1]["type"], "tool")

        # Get context with tool messages
        filtered_context = Context.transform_to_filtered_context(context, show_tool_calls=True)
        print(json.dumps(filtered_context.model_dump(), indent=4))

        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)
        Tool.delete_tool(tool.tool_id)

    def test_get_context_with_system_messages(self):
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)

        agent = Agent.create_agent(
            agent_name="test-agent",
            agent_description="test agent",
            prompt="You are a flight assistant.",
            org_id=user.organizations[0],
            agent_speaks_first=False,
            is_public=False
        )

        context = Context.create_context(agent.agent_id, cognito_user.sub)

        # Create the AgentChat
        agent_chat = AgentChat(
            llm=create_llm(),
            prompt=agent.prompt,
            messages=context.messages,
            tools=[],
            context=context.model_dump()
        )

        # Add human message
        agent_chat.add_human_message_and_invoke("What is the flight status for flight AA123? And where is it going?")
        # Save the context after adding the human message
        context.messages = base_messages_to_dict_messages(agent_chat.messages)

        # Add a system message
        context = Context.add_system_message(context, "Sell them possible bike tours in the destination of the flight.")

        # Create the agent chat again with the updated context
        agent_chat = AgentChat(
            llm=create_llm(),
            prompt=agent.prompt,
            messages=dict_messages_to_base_messages(context.messages),
            tools=[],
            context=context.model_dump()
        )

        # Invoke the agent chat
        agent_chat.invoke()
        # Save the context after invoking the agent chat
        context.messages = base_messages_to_dict_messages(agent_chat.messages)
        Context.save_context(context)

        # Get the context with system messages
        request = create_request(
            method="GET",
            path=f"/context/{context.context_id}",
            headers={
                "Authorization": access_token
            },
        )

        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)

        res_body = json.loads(result["body"])
        print(json.dumps(res_body, indent=4))
        self.assertTrue(any(msg["sender"] == "system" for msg in res_body["messages"]))

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_create_context_with_user_defined_data(self):
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            agent_name="test-agent",
            agent_description="agent with user defined data",
            prompt="You are a helpful assistant.",
            org_id=user.organizations[0],
            agent_speaks_first=False,
            is_public=False
        )

        # body
        body = {
            "agent_id": agent.agent_id,
            "user_defined": {
                "name": "Alice"
            }
        }

        # Create request
        request = create_request(
            method="POST",
            path="/context",
            headers={
                "Authorization": access_token
            },
            body=body
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        res_body = json.loads(result["body"])
        print(json.dumps(res_body, indent=4))

        # Clean up 
        Context.delete_context(res_body["context_id"])
        Agent.delete_agent(agent.agent_id)

    def test_add_messages(self):
        """Test adding messages to a context"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-add-messages",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="You are a helpful assistant.",
            tools=[]
        )
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Record initial message count
        initial_message_count = len(context.messages)

        # Create messages to add
        messages_to_add = [
            {
                "sender": "human",
                "message": "Hello, how are you?"
            },
            {
                "sender": "ai",
                "message": "I'm doing well, thank you for asking!"
            }
        ]

        # Create the request
        request = create_request(
            method="POST",
            path="/context/add-messages",
            body={
                "context_id": context.context_id,
                "messages": messages_to_add
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        
        # Verify response structure
        self.assertIn("context_id", response)
        self.assertIn("messages", response)
        self.assertEqual(response["context_id"], context.context_id)
        
        # Verify messages were added
        self.assertEqual(len(response["messages"]), initial_message_count + 2)
        
        # Verify the new messages are in the response
        last_two_messages = response["messages"][-2:]
        self.assertEqual(last_two_messages[0]["sender"], "human")
        self.assertEqual(last_two_messages[0]["message"], "Hello, how are you?")
        self.assertEqual(last_two_messages[1]["sender"], "ai")
        self.assertEqual(last_two_messages[1]["message"], "I'm doing well, thank you for asking!")

        # Verify messages were saved to the database
        updated_context = Context.get_context(context.context_id)
        self.assertEqual(len(updated_context.messages), initial_message_count + 2)

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_set_messages(self):
        """Test replacing all messages in a context"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-set-messages",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="You are a helpful assistant.",
            tools=[]
        )
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Add some initial messages
        Context.add_ai_message(context, "Initial message 1")
        Context.add_ai_message(context, "Initial message 2")
        
        # Refresh context to get updated messages
        context = Context.get_context(context.context_id)
        initial_message_count = len(context.messages)
        self.assertGreater(initial_message_count, 0)

        # Create new messages to replace all existing ones
        new_messages = [
            {
                "sender": "human",
                "message": "New conversation start"
            },
            {
                "sender": "ai",
                "message": "Hello! This is a fresh start."
            }
        ]

        # Create the request
        request = create_request(
            method="POST",
            path="/context/set-messages",
            body={
                "context_id": context.context_id,
                "messages": new_messages
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the lambda handler
        result = lambda_handler(request, None)

        # Check the response
        self.assertEqual(result["statusCode"], 200)
        response = json.loads(result["body"])
        
        # Verify response structure
        self.assertIn("context_id", response)
        self.assertIn("messages", response)
        self.assertEqual(response["context_id"], context.context_id)
        
        # Verify all messages were replaced (should only have 2 new messages)
        self.assertEqual(len(response["messages"]), 2)
        self.assertEqual(response["messages"][0]["sender"], "human")
        self.assertEqual(response["messages"][0]["message"], "New conversation start")
        self.assertEqual(response["messages"][1]["sender"], "ai")
        self.assertEqual(response["messages"][1]["message"], "Hello! This is a fresh start.")

        # Verify messages were saved to the database
        updated_context = Context.get_context(context.context_id)
        self.assertEqual(len(updated_context.messages), 2)

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

    def test_generate_without_saving_then_add_messages(self):
        """Test the workflow of generating messages without saving, then adding them via add-messages endpoint"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        agent = Agent.create_agent(
            org_id=user.organizations[0],
            agent_name="test-agent-generate-then-add",
            is_public=False,
            agent_speaks_first=False,
            agent_description="test-agent-description",
            prompt="Call the pass_event tool with type 'approval_test' and data 'pending_approval'",
            tools=["pass_event"]
        )
        context = Context.create_context(
            agent_id=agent.agent_id,
            user_id=user.user_id
        )

        # Record initial message count
        initial_message_count = len(context.messages)

        # Step 1: Generate messages without saving
        chat_request = create_request(
            method="POST",
            path="/chat",
            body={
                "context_id": context.context_id,
                "message": "Please proceed",
                "save_ai_messages": False
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the chat handler
        chat_result = lambda_handler(chat_request, None)
        self.assertEqual(chat_result["statusCode"], 200)
        chat_response = json.loads(chat_result["body"])
        
        # Verify AI messages were NOT saved
        self.assertEqual(chat_response["saved_ai_messages"], False)
        self.assertIn("generated_messages", chat_response)
        self.assertGreater(len(chat_response["generated_messages"]), 0)
        
        # Verify context has the human message but not the AI-generated messages
        context_after_chat = Context.get_context(context.context_id)
        self.assertEqual(len(context_after_chat.messages), initial_message_count + 1,
                        "Human message should be saved even when save_ai_messages=False")

        # Step 2: "Approve" and add the generated messages
        # The human message is already saved, so we only need to add the AI-generated messages
        messages_to_add = chat_response["generated_messages"]

        add_messages_request = create_request(
            method="POST",
            path="/context/add-messages",
            body={
                "context_id": context.context_id,
                "messages": messages_to_add
            },
            headers={
                "Authorization": access_token
            }
        )

        # Call the add messages handler
        add_result = lambda_handler(add_messages_request, None)
        self.assertEqual(add_result["statusCode"], 200)
        add_response = json.loads(add_result["body"])

        # Verify messages were added
        self.assertGreater(len(add_response["messages"]), initial_message_count)
        
        # Verify the messages are now saved in the database
        final_context = Context.get_context(context.context_id)
        # Expected: initial + human message (already saved) + generated messages (just added)
        expected_message_count = initial_message_count + 1 + len(messages_to_add)
        self.assertEqual(len(final_context.messages), expected_message_count)

        # Verify the complete conversation is in the context
        filtered_context = Context.transform_to_filtered_context(final_context, show_tool_calls=True)
        human_messages = [msg for msg in filtered_context.messages if hasattr(msg, 'sender') and msg.sender == 'human']
        self.assertGreater(len(human_messages), 0)
        self.assertEqual(human_messages[-1].message, "Please proceed")
        
        # Verify we have tool calls and responses
        tool_calls = [msg for msg in filtered_context.messages if hasattr(msg, 'type') and msg.type == 'tool_call']
        tool_responses = [msg for msg in filtered_context.messages if hasattr(msg, 'type') and msg.type == 'tool_response']
        self.assertGreater(len(tool_calls), 0, "Should have tool calls in the final context")
        self.assertGreater(len(tool_responses), 0, "Should have tool responses in the final context")

        # Clean up
        Context.delete_context(context.context_id)
        Agent.delete_agent(agent.agent_id)

