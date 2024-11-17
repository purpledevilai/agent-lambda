import os
from datetime import datetime
import uuid
from AWS.DynamoDBFunctions import get_item, put_item

ORGANIZATIONS_TABLE_NAME = os.environ["ORGANIZATIONS_TABLE_NAME"]
ORGANIZATIONS_PRIMARY_KEY = os.environ["ORGANIZATIONS_PRIMARY_KEY"]


def organization_exists(organization_id: str) -> bool:
    try:
        get_item(ORGANIZATIONS_TABLE_NAME, ORGANIZATIONS_PRIMARY_KEY, organization_id)
        return True
    except:
        return False


def create_organization(organization_name: str) -> dict:
    organization = {
        ORGANIZATIONS_PRIMARY_KEY: str(uuid.uuid4()),
        "name": organization_name,
        "users": [],
        "created_at": int(datetime.timestamp(datetime.now())),
        "updated_at": int(datetime.timestamp(datetime.now())),
    }
    put_item(ORGANIZATIONS_TABLE_NAME, organization)
    return organization


def get_organization(organization_id: str) -> dict:
    try:
        return get_item(ORGANIZATIONS_TABLE_NAME, ORGANIZATIONS_PRIMARY_KEY, organization_id)
    except:
        raise Exception(f"Organization with id: {organization_id} does not exist")
    
def save_organization(organization: dict) -> dict:
    put_item(ORGANIZATIONS_TABLE_NAME, organization)

def associate_user_with_organization(organization_id: str, user_id: str) -> dict:
    organization = get_organization(organization_id)
    organization["users"].append(user_id)
    save_organization(organization)
    return organization

def user_belongs_to_organization(organization_id: str, user_id: str) -> bool:
    organization = get_organization(organization_id)
    return user_id in organization["users"]



