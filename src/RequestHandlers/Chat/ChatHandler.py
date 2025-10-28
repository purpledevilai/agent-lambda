import json
from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User, Context, Chat, Tool
from LLM.AgentChat import AgentChat
from LLM.CreateLLM import create_llm
from LLM.BaseMessagesConverter import dict_messages_to_base_messages, base_messages_to_dict_messages


def chat_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Agent.Agent:  

    # Get the body of the request
    body = Chat.ChatInput(**json.loads(lambda_event.body))
    
    # Get the context and agent
    context = None
    agent = None
    if (user):
        db_user = User.get_user(user.sub)
        context = Context.get_context_for_user(body.context_id, db_user.user_id)
        agent = Agent.get_agent_for_user(context.agent_id, db_user)
    else:
        context = Context.get_public_context(body.context_id)
        agent = Agent.get_public_agent(context.agent_id)

    # Add the human message to the context and save it immediately
    context = Context.add_human_message(context, body.message)

    # Context dict for context updates (after human message is added)
    context_dict = context.model_dump()

    # Capture the number of messages before AI generation
    messages_before_generation = len(context.messages)

    # Create the agent chat with the updated context (including human message)
    agent_chat = AgentChat(
        create_llm(),
        agent.prompt,
        messages=dict_messages_to_base_messages(context.messages),
        tools=[Tool.get_agent_tool_with_id(tool) for tool in agent.tools] if agent.tools else [],
        context=context_dict
    )

    # Invoke the agent (human message already in context)
    agent_response = agent_chat.invoke()

    # Convert all messages to dict format
    all_dict_messages = base_messages_to_dict_messages(agent_chat.messages)
    
    # Extract generated messages (everything after the human message)
    generated_dict_messages = all_dict_messages[messages_before_generation:]
    
    # Transform generated messages to filtered format (with tool calls shown)
    generated_filtered_messages = Context.transform_messages_to_filtered(
        generated_dict_messages, 
        show_tool_calls=True
    )
    
    # Convert filtered messages to dicts for JSON serialization
    generated_messages_dicts = [msg.model_dump() for msg in generated_filtered_messages]

    # Conditionally save AI-generated messages based on save_ai_messages flag
    if body.save_ai_messages:
        context.messages = all_dict_messages
        Context.save_context(context)

    # Initialize the response
    response = Chat.ChatResponse(
        response=agent_response,
        saved_ai_messages=body.save_ai_messages,
        generated_messages=generated_messages_dicts
    )

    # check if there are chat events
    if (context_dict.get("events")):
        response.events = context_dict["events"]
    
    return response