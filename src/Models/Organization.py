import os
from datetime import datetime
import uuid
from src.AWS.DynamoDB import get_item, put_item, delete_item
from pydantic import BaseModel

ORGANIZATIONS_TABLE_NAME = os.environ["ORGANIZATIONS_TABLE_NAME"]
ORGANIZATIONS_PRIMARY_KEY = os.environ["ORGANIZATIONS_PRIMARY_KEY"]

class Organization(BaseModel):
    org_id: str
    name: str
    users: list[str]


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


def get_organization(organization_id: str) -> Organization:
    item = get_item(ORGANIZATIONS_TABLE_NAME, ORGANIZATIONS_PRIMARY_KEY, organization_id)
    if item is None:
        raise Exception(f"Organization with id: {organization_id} does not exist")
    return Organization(**item)
    
def save_organization(organization: Organization):
    put_item(ORGANIZATIONS_TABLE_NAME, organization.model_dump())

def delete_organization(organization_id: str) -> None:
    delete_item(ORGANIZATIONS_TABLE_NAME, ORGANIZATIONS_PRIMARY_KEY, organization_id)

def associate_user_with_organization(organization_id: str, user_id: str) -> dict:
    organization = get_organization(organization_id)
    organization["users"].append(user_id)
    save_organization(organization)
    return organization

def user_belongs_to_organization(organization_id: str, user_id: str) -> bool:
    organization = get_organization(organization_id)
    return user_id in organization["users"]

def remove_user_from_organization(organization_id: str, user_id: str) -> Organization:
    organization = get_organization(organization_id)
    organization.users.remove(user_id)
    save_organization(organization)
    return organization



