from Agent.Context import get_contexts_by_user_id

def get_chat_history_handler(user_id):
    chat_history = get_contexts_by_user_id(user_id)
    # Reverse sort by time_stamp
    chat_history = sorted(chat_history, key=lambda x: x["time_stamp"], reverse=True)
    # Take out the messages from the context
    chat_history = [{
        "context_id": context["context_id"],
        "first_message": context["messages"][0]["content"] if len(context["messages"]) > 0 else "No messages",
    } for context in chat_history]
    return { "chat_history": chat_history }