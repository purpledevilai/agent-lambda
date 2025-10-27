import json
from typing import Optional
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User, Context, Chat, Tool
from LLM.AgentChat import AgentChat
from LLM.CreateLLM import create_llm
from LLM.BaseMessagesConverter import dict_messages_to_base_messages, base_messages_to_dict_messages


class AddAIMessageInput(BaseModel):
    context_id: str
    message: Optional[str] = None
    prompt: Optional[str] = None


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

    # If message just add it to the context and return
    if body.message:
        # Add it as an AI message to the context
        Context.add_ai_message(context=context, message=body.message)
        # Return the message - no generated messages since we're just adding a pre-written message
        return Chat.ChatResponse(
            response=body.message,
            saved_messages=True,
            generated_messages=[]
        )
    
    # Otherwise, if prompt is provided, append it to the agent's prompt
    if not body.prompt:
        raise ValueError("Either 'message' or 'prompt' must be provided in the request body.")
    
    context = Context.add_system_message(context=context, message=body.prompt)

    # Context dict for context updates
    context_dict = context.model_dump()

    # Capture the number of messages before generation
    messages_before_count = len(context.messages)

    # Create the agent chat
    agent_chat = AgentChat(
        llm=create_llm(),
        prompt=agent.prompt,
        messages=dict_messages_to_base_messages(context.messages),
        tools=[Tool.get_agent_tool_with_id(tool) for tool in agent.tools] if agent.tools else [],
        context=context_dict
    )

    # Invoke the agent (no human message added)
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

    # Save the new messages to context
    context.messages = all_dict_messages
    Context.save_context(context)

    # Initialize the response
    response = Chat.ChatResponse(
        response=agent_response,
        saved_messages=True,
        generated_messages=generated_messages_dicts
    )

    # check if there are chat events
    if (context_dict.get("events")):
        response.events = context_dict["events"]
    
    return response