from LLM.AgentChat import AgentChat
from LLM.CreateLLM import create_llm
from Models.Context import get_context_for_user, save_context
from Models.Agent import get_agent_for_user
from LLM.BaseMessagesConverter import dict_messages_to_base_messages, base_messages_to_dict_messages

def agent_message_handler(message, context_id, user_id):

    # Get the context
    context = get_context_for_user(context_id, user_id)

    # Get the agent
    agent = get_agent_for_user(context["agent_id"], user_id)

    # Create the agent chat
    agent = AgentChat(
        create_llm(),
        agent["prompt"],
        messages=dict_messages_to_base_messages(context["messages"])
    )

    # Add the human message and invoke the agent
    response = agent.add_human_message_and_invoke(message)

    # Save the new message to context
    context["messages"] = base_messages_to_dict_messages(agent.messages)
    save_context(context)
    
    return { "response": response }