from Agent.Agent import Agent
from LLM.CreateLLM import create_llm
from Agent.Context import get_context, save_context
from Agent.BaseMessagesConverter import dict_messages_to_base_messages, base_messages_to_dict_messages

def agent_message_handler(agent_name, message, context_id, user_id):

    # Get the context
    context = get_context(context_id, user_id)

    # Get the agent
    agent = Agent(
        create_llm(),
        "You are a helpful assistant.",
        messages=dict_messages_to_base_messages(context["messages"])
    )

    # Add the human message and invoke the agent
    response = agent.add_human_message_and_invoke(message)

    # Save the context
    context["messages"] = base_messages_to_dict_messages(agent.messages)
    save_context(context)
    
    return { "response": response, "context_id": context_id }