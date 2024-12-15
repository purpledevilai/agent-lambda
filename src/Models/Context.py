import os
from datetime import datetime
import uuid
from AWS.DynamoDBFunctions import get_item, put_item, get_all_items_by_index, delete_item

CONTEXTS_TABLE_NAME = os.environ["CONTEXTS_TABLE_NAME"]
CONTEXTS_PRIMARY_KEY = os.environ["CONTEXTS_PRIMARY_KEY"]

def context_exists(context_id: str) -> dict:
    try: 
        get_item(CONTEXTS_TABLE_NAME, CONTEXTS_PRIMARY_KEY, context_id)
        return True
    except:
        return False
    
def create_context(agent_id: str, user_id: str):
    context = {
        CONTEXTS_PRIMARY_KEY: str(uuid.uuid4()),
        "agent_id": agent_id,
        "user_id": user_id if user_id is not None else "public",
        "time_stamp": int(datetime.timestamp(datetime.now())),
        "messages": []
    }
    put_item(CONTEXTS_TABLE_NAME, context)
    return context


def get_context(context_id: str) -> dict:
    try:
        return get_item(CONTEXTS_TABLE_NAME, CONTEXTS_PRIMARY_KEY, context_id)
    except:
        raise Exception(f"Context with id: {context_id} does not exist")
    
def get_context_for_user(context_id: str, user_id: str) -> dict:
    context = get_context(context_id)
    if (context.get("user_id") == "public"):
        return context
    if (context.get("user_id") == user_id):
        return context
    raise Exception(f"Context does not belong to user")

def save_context(context: dict) -> None:
    put_item(CONTEXTS_TABLE_NAME, context)

def get_contexts_by_user_id(user_id: str) -> list[dict]:
    return get_all_items_by_index(CONTEXTS_TABLE_NAME, "user_id", user_id)

def delete_context(context_id: str):
    delete_item(CONTEXTS_TABLE_NAME, CONTEXTS_PRIMARY_KEY, context_id)
    

