from Models.User import create_user, user_exists

def create_user_handler(user_id: str) -> dict:
    if user_exists(user_id):
        raise Exception(f"User with id: {user_id} already exists")
    return create_user(user_id)
