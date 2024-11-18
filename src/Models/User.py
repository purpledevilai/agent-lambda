import os
from datetime import datetime
import uuid
from AWS.DynamoDBFunctions import get_item, put_item

USERS_TABLE_NAME = os.environ["USERS_TABLE_NAME"]
USERS_PRIMARY_KEY = os.environ["USERS_PRIMARY_KEY"]


def user_exists(user_id: str) -> bool:
    try:
        get_item(USERS_TABLE_NAME, USERS_PRIMARY_KEY, user_id)
        return True
    except:
        return False


def create_user(user_id: str) -> dict:
    user = {
        USERS_PRIMARY_KEY: user_id,
        "organizations": [],
        "created_at": int(datetime.timestamp(datetime.now())),
        "updated_at": int(datetime.timestamp(datetime.now())),
    }
    put_item(USERS_TABLE_NAME, user)
    return user


def get_user(user_id: str) -> dict:
    try:
        return get_item(USERS_TABLE_NAME, USERS_PRIMARY_KEY, user_id)
    except:
        raise Exception(f"User with id: {user_id} does not exist")
    
def save_user(user: dict) -> dict:
    put_item(USERS_TABLE_NAME, user)

def associate_organization_with_user(user_id: str, organization_id: str,) -> dict:
    user = get_user(user_id)
    user["organizations"].append(organization_id)
    save_user(user)
    return user

def user_is_member_of_organization(user_id: str, organization_id: str) -> bool:
    user = get_user(user_id)
    return organization_id in user["organizations"]


