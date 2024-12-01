from LLM.AgentChat import AgentChat
from LLM.CreateLLM import create_llm
from LLM.BaseMessagesConverter import dict_messages_to_base_messages, base_messages_to_dict_messages
from Models.Context import get_context, save_context

def context_invoke(context, agent):
    agent = AgentChat(
        create_llm(),
        agent["prompt"],
        messages=dict_messages_to_base_messages(context["messages"])
    )
    agent.invoke()

    # Save the new message to context
    context["messages"] = base_messages_to_dict_messages(agent.messages)
    save_context(context)

    return context