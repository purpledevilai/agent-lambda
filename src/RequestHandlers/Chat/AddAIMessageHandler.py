import json
from typing import Optional
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User, Context, Chat, Tool
from LLM.AgentChat import AgentChat
from LLM.CreateLLM import create_llm
from LLM.BaseMessagesConverter import dict_messages_to_base_messages, base_messages_to_dict_messages
from LLM.TerminatingConfig import TerminatingConfig


class AddAIMessageInput(BaseModel):
    context_id: str
    message: Optional[str] = None
    prompt: Optional[str] = None
    save_ai_messages: Optional[bool] = True
    save_system_message: Optional[bool] = True
    terminating_config: Optional[TerminatingConfig] = None


def add_ai_message_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Agent.Agent:  

    # Get the body of the request
    body = AddAIMessageInput(**json.loads(lambda_event.body))
    
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

    # Process any pending async tool responses
    context = Context.process_async_tool_response_queue(context)
    
    # If message just add it to the context and return
    if body.message:
        # Add it as an AI message to the context
        Context.add_ai_message(context=context, message=body.message)
        # Return the message - no generated messages since we're just adding a pre-written message
        # Note: save_ai_messages doesn't apply here since we're manually adding a message (always saved)
        return Chat.ChatResponse(
            response=body.message,
            saved_ai_messages=True,
            generated_messages=[]
        )
    
    # Otherwise, if prompt is provided, append it to the agent's prompt
    if not body.prompt:
        raise ValueError("Either 'message' or 'prompt' must be provided in the request body.")
    
    # Track the message count before adding the system message
    messages_before_system = len(context.messages)
    
    # Add system message with the prompt (this saves immediately)
    context = Context.add_system_message(context=context, message=body.prompt)
    
    # Save the index of the system message we just added
    system_message_index = messages_before_system

    # Context dict for context updates
    context_dict = context.model_dump()

    # Capture the number of messages before AI generation (includes system message)
    messages_before_generation = len(context.messages)

    # Combine agent tools with context additional_agent_tools (remove duplicates)
    agent_tool_ids = agent.tools if agent.tools else []
    context_tool_ids = context.additional_agent_tools if context.additional_agent_tools else []
    combined_tool_ids = list(dict.fromkeys(agent_tool_ids + context_tool_ids))  # Preserve order, remove duplicates
    
    # Get tool objects
    tools = [Tool.get_agent_tool_with_id(tool_id) for tool_id in combined_tool_ids] if combined_tool_ids else []

    # Create the agent chat
    agent_chat = AgentChat(
        llm=create_llm(),
        prompt=agent.prompt,
        messages=dict_messages_to_base_messages(context.messages),
        tools=tools,
        context=context_dict,
        prompt_arg_names=agent.prompt_arg_names if agent.prompt_arg_names else [],
        terminating_config=body.terminating_config
    )

    # Invoke the agent (no human message added)
    agent_response = agent_chat.invoke()

    # Convert all messages to dict format
    all_dict_messages = base_messages_to_dict_messages(agent_chat.messages)
    
    # Extract generated messages (everything after the system message was added)
    generated_dict_messages = all_dict_messages[messages_before_generation:]
    
    # Transform generated messages to filtered format (with tool calls shown)
    generated_filtered_messages = Context.transform_messages_to_filtered(
        generated_dict_messages, 
        show_tool_calls=True
    )
    
    # Convert filtered messages to dicts for JSON serialization
    generated_messages_dicts = [msg.model_dump() for msg in generated_filtered_messages]

    # Reload context from database to get the current saved state (with system message)
    if user:
        context = Context.get_context_for_user(body.context_id, db_user.user_id)
    else:
        context = Context.get_public_context(body.context_id)
    
    # Handle saving logic based on flags
    # At this point, context has: [original messages] + [system message]
    # all_dict_messages has: [original messages] + [system message] + [AI generated messages]
    
    # Case 1: save_system_message=True, save_ai_messages=True -> Save everything
    # Case 2: save_system_message=True, save_ai_messages=False -> Keep only up to system message (clear AI messages)
    # Case 3: save_system_message=False, save_ai_messages=True -> Remove system message, save AI messages
    # Case 4: save_system_message=False, save_ai_messages=False -> Clear back to before system message
    
    if body.save_system_message and body.save_ai_messages:
        # Case 1: Save everything (system message + AI messages)
        context.messages = all_dict_messages
        Context.save_context(context)
    elif body.save_system_message and not body.save_ai_messages:
        # Case 2: Keep only up to system message (already saved), clear everything after
        # Context already has messages up to and including system message, just need to ensure no AI messages
        context.messages = all_dict_messages[:messages_before_generation]
        Context.save_context(context)
    elif not body.save_system_message and body.save_ai_messages:
        # Case 3: Remove system message, keep AI messages
        # Take messages before system + AI messages after system
        messages_to_save = all_dict_messages[:system_message_index] + all_dict_messages[messages_before_generation:]
        context.messages = messages_to_save
        Context.save_context(context)
    else:
        # Case 4: Remove system message and don't save AI messages (clear back to before system message)
        context.messages = all_dict_messages[:system_message_index]
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