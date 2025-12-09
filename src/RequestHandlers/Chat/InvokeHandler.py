import json
from typing import Optional
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User, Context, Chat, Tool
from LLM.AgentChat import AgentChat
from LLM.CreateLLM import create_llm
from LLM.BaseMessagesConverter import dict_messages_to_base_messages, base_messages_to_dict_messages


class InvokeInput(BaseModel):
    context_id: str
    save_ai_messages: Optional[bool] = True


def invoke_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Chat.ChatResponse:
    """
    Invoke the agent without adding a human message.
    Useful after manually setting up tool calls or for continuing from existing messages.
    """
    # Get the body of the request
    body = InvokeInput(**json.loads(lambda_event.body))
    
    # Get the context and agent
    context = None
    agent = None
    if user:
        db_user = User.get_user(user.sub)
        context = Context.get_context_for_user(body.context_id, db_user.user_id)
        agent = Agent.get_agent_for_user(context.agent_id, db_user)
    else:
        context = Context.get_public_context(body.context_id)
        agent = Agent.get_public_agent(context.agent_id)

    # Process any pending async tool responses
    context = Context.process_async_tool_response_queue(context)

    # Context dict for context updates
    context_dict = context.model_dump()

    # Capture the number of messages before generation
    messages_before_count = len(context.messages)

    # Combine agent tools with context additional_agent_tools (remove duplicates)
    agent_tool_ids = agent.tools if agent.tools else []
    context_tool_ids = context.additional_agent_tools if context.additional_agent_tools else []
    combined_tool_ids = list(dict.fromkeys(agent_tool_ids + context_tool_ids))  # Preserve order, remove duplicates
    
    # Get tool objects
    tools = [Tool.get_agent_tool_with_id(tool_id) for tool_id in combined_tool_ids] if combined_tool_ids else []

    # Create the agent chat
    agent_chat = AgentChat(
        create_llm(),
        agent.prompt,
        messages=dict_messages_to_base_messages(context.messages),
        tools=tools,
        context=context_dict
    )

    # Invoke the agent without adding a human message
    agent_response = agent_chat.invoke()

    # Convert all messages to dict format
    all_dict_messages = base_messages_to_dict_messages(agent_chat.messages)
    
    # Extract generated messages (everything after the original messages)
    generated_dict_messages = all_dict_messages[messages_before_count:]
    
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
    if context_dict.get("events"):
        response.events = context_dict["events"]
    
    return response

