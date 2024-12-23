import json
from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User, Context, Chat
import Tools
import Tools.SetPrompt
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

    # Set up tools
    tools = []
    if (agent.tools):
        for tool in agent.tools:
            if (tool == "set-prompt"):
                tools.append(Tools.SetPrompt.set_prompt_tool)

    # Context dict for context updates
    context_dict = context.model_dump()

    # Create the agent chat
    agent = AgentChat(
        create_llm(),
        agent.prompt,
        messages=dict_messages_to_base_messages(context.messages),
        tools=tools,
        context=context_dict
    )

    # Add the human message and invoke the agent
    agent_response = agent.add_human_message_and_invoke(body.message)

    # Initialize the response
    response = Chat.ChatResponse(response=agent_response)

    # Save the new message to context
    context.messages = base_messages_to_dict_messages(agent.messages)
    Context.save_context(context)

    # check if there are ui updates
    if (context_dict.get("ui_updates")):
        response.events = context_dict["ui_updates"]
    
    return response