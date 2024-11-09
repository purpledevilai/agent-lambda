from AWS.DynamoDBFunctions import get_item, put_item
import os

CONTEXTS_TABLE_NAME = os.environ["CONTEXTS_TABLE_NAME"]
CONTEXTS_PRIMARY_KEY = os.environ["CONTEXTS_PRIMARY_KEY"]

def get_context(context_id: str) -> dict:
    try:
        context = get_item(CONTEXTS_TABLE_NAME, CONTEXTS_PRIMARY_KEY, context_id)
    except:
        context = {
            "context_id": context_id,
            "messages": []
        }
    return context

def save_context(context: dict) -> None:
    put_item(CONTEXTS_TABLE_NAME, context)

