from Agent.Context import get_contexts_by_user_id
from Agent.Agent import get_agents_for_user

def get_chat_history_handler(user_id):
    chat_history = get_contexts_by_user_id(user_id)
    # Reverse sort by time_stamp
    chat_history = sorted(chat_history, key=lambda x: x["time_stamp"], reverse=True)
    # Get the user's agents
    agents = get_agents_for_user(user_id)
    agent_dict = { agent["agent_id"]: agent for agent in agents }
    # Take out the messages from the context
    chat_history = [{
        "context_id": context["context_id"],
        "title": agent_dict[context["agent_id"]]["agent_name"],
    } for context in chat_history]
    return { "chat_history": chat_history }