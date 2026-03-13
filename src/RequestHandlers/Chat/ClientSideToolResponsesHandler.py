import json
from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User, Context, Chat, Tool
from Models.TokenTracking import InvocationTokenTracker
from Models.LLMModel import get_model_or_none
from LLM.AgentChat import AgentChat
from LLM.CreateLLM import create_llm, DEFAULT_MODEL
from LLM.BaseMessagesConverter import dict_messages_to_base_messages, base_messages_to_dict_messages
from langchain_core.messages import AIMessage, ToolMessage


def client_side_tool_responses_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Chat.ChatResponse:

    # Get the body of the request
    body = Chat.ClientSideToolResponsesInput(**json.loads(lambda_event.body))

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

    # Combine agent tools with context additional_agent_tools (remove duplicates)
    agent_tool_ids = agent.tools if agent.tools else []
    context_tool_ids = context.additional_agent_tools if context.additional_agent_tools else []
    combined_tool_ids = list(dict.fromkeys(agent_tool_ids + context_tool_ids))

    # Get tool objects
    tools = [Tool.get_agent_tool_with_id(tool_id) for tool_id in combined_tool_ids] if combined_tool_ids else []

    # Create token tracker for this invocation
    token_tracker = InvocationTokenTracker(agent.org_id, context.model_id)

    # Build base messages from context
    messages = dict_messages_to_base_messages(context.messages)

    # Create the agent chat (needed for name_to_tool_id mapping)
    agent_chat = AgentChat(
        create_llm(context.model_id),
        agent.prompt,
        messages=messages,
        tools=tools,
        context=context_dict,
        prompt_arg_names=agent.prompt_arg_names if agent.prompt_arg_names else [],
        on_response=token_tracker.on_response,
    )

    # Find the last AIMessage with tool_calls
    last_ai_with_tools = None
    for message in reversed(agent_chat.messages):
        if isinstance(message, AIMessage) and message.tool_calls:
            last_ai_with_tools = message
            break

    if not last_ai_with_tools:
        raise Exception("No AIMessage with tool_calls found in context", 400)

    # Identify which tool_calls in that message are client-side
    client_side_tool_call_ids = set()
    for tool_call in last_ai_with_tools.tool_calls:
        tool_name = tool_call["name"]
        tool = agent_chat.name_to_tool.get(tool_name)
        if tool and tool.is_client_side_tool:
            client_side_tool_call_ids.add(tool_call["id"])

    if not client_side_tool_call_ids:
        raise Exception("No client-side tool calls found in the last AIMessage", 400)

    # Validate that ALL client-side tool calls have a response
    response_map = {tr.tool_call_id: tr.response for tr in body.tool_responses}
    missing = client_side_tool_call_ids - set(response_map.keys())
    if missing:
        raise Exception(f"Missing responses for client-side tool call IDs: {missing}", 400)

    # Capture message count before adding tool responses
    messages_before_generation = len(agent_chat.messages)

    # Append ToolMessages for each client-side tool response
    for tool_call in last_ai_with_tools.tool_calls:
        if tool_call["id"] in client_side_tool_call_ids:
            agent_chat.messages.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=response_map[tool_call["id"]]
                )
            )

    # Continue invocation
    agent_response = agent_chat.invoke()

    # Convert all messages to dict format
    all_dict_messages = base_messages_to_dict_messages(agent_chat.messages)

    # Extract generated messages (tool responses + everything after)
    generated_dict_messages = all_dict_messages[messages_before_generation:]

    # Transform generated messages to filtered format
    generated_filtered_messages = Context.transform_messages_to_filtered(
        generated_dict_messages,
        show_tool_calls=True
    )

    generated_messages_dicts = [msg.model_dump() for msg in generated_filtered_messages]

    # Save context
    context.messages = all_dict_messages
    Context.save_context(context)

    # Calculate context percentage and invocation cost
    effective_model_id = context.model_id or DEFAULT_MODEL
    context_percentage = None
    invocation_cost = None
    llm_model = get_model_or_none(effective_model_id)
    if llm_model:
        if llm_model.context_window_size:
            context_size = agent_chat.get_context_size()
            context_percentage = round((context_size / llm_model.context_window_size) * 100, 2)
        invocation_cost = token_tracker.calculate_cost(llm_model.input_token_cost, llm_model.output_token_cost)

    response = Chat.ChatResponse(
        response=agent_response,
        saved_ai_messages=True,
        generated_messages=generated_messages_dicts,
        model_id=effective_model_id,
        context_percentage=context_percentage,
        invocation_cost=invocation_cost,
    )

    # Check for pending client-side tool calls (another round)
    if agent_chat.pending_client_side_tool_calls:
        response.client_side_tool_calls = [
            Chat.ClientSideToolCall(**tc) for tc in agent_chat.pending_client_side_tool_calls
        ]

    # Check if there are chat events
    if context_dict.get("events"):
        response.events = context_dict["events"]

    return response
