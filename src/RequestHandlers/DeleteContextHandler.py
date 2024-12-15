from Models.Context import get_context_for_user, delete_context

def delete_context_handler(context_id: str, user_id: str) -> dict:
    context = get_context_for_user(context_id, user_id)
    delete_context(context["context_id"])
    return {
        "success": f"Context with id: {context_id} has been deleted"
    }
