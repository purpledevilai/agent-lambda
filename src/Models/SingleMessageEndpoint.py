import os
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from AWS.DynamoDB import get_item, put_item, delete_item, get_all_items_by_index
from Models import User

SME_TABLE_NAME = os.environ["SME_TABLE_NAME"]
SME_PRIMARY_KEY = os.environ["SME_PRIMARY_KEY"]


class SingleMessageEndpoint(BaseModel):
    sme_id: str
    org_id: str
    name: str
    description: Optional[str] = None
    pd_id: str
    is_public: bool
    created_at: int
    updated_at: int


class CreateSMEParams(BaseModel):
    org_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    pd_id: str
    is_public: bool = False


class UpdateSMEParams(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pd_id: Optional[str] = None
    is_public: Optional[bool] = None


def sme_exists(sme_id: str) -> bool:
    return get_item(SME_TABLE_NAME, SME_PRIMARY_KEY, sme_id) is not None


def create_sme(org_id: str, name: str, description: Optional[str], pd_id: str, is_public: bool = False) -> SingleMessageEndpoint:
    sme_id = str(uuid.uuid4())
    created_at = int(datetime.now().timestamp())
    updated_at = created_at
    sme = SingleMessageEndpoint(
        sme_id=sme_id,
        org_id=org_id,
        name=name,
        description=description,
        pd_id=pd_id,
        is_public=is_public,
        created_at=created_at,
        updated_at=updated_at
    )
    put_item(SME_TABLE_NAME, sme.model_dump())
    return sme


def get_sme(sme_id: str) -> SingleMessageEndpoint:
    item = get_item(SME_TABLE_NAME, SME_PRIMARY_KEY, sme_id)
    if item is None:
        raise Exception(f"SME {sme_id} not found", 404)
    return SingleMessageEndpoint(**item)


def get_public_sme(sme_id: str) -> SingleMessageEndpoint:
    sme = get_sme(sme_id)
    if not sme.is_public:
        raise Exception(f"SME {sme_id} is not public", 403)
    return sme


def get_sme_for_org(sme_id: str, org_id: str) -> SingleMessageEndpoint:
    sme = get_sme(sme_id)
    if sme.org_id != org_id:
        raise Exception(f"SME {sme_id} not found for org", 404)
    return sme


def get_sme_for_user(sme_id: str, user: User.User) -> SingleMessageEndpoint:
    sme = get_sme(sme_id)
    if sme.is_public:
        return sme
    if sme.org_id not in user.organizations:
        raise Exception(f"SME does not belong to user's orgs", 403)
    return sme


def save_sme(sme: SingleMessageEndpoint) -> SingleMessageEndpoint:
    sme.updated_at = int(datetime.now().timestamp())
    put_item(SME_TABLE_NAME, sme.model_dump())
    return sme


def delete_sme(sme_id: str) -> None:
    delete_item(SME_TABLE_NAME, SME_PRIMARY_KEY, sme_id)


def get_smes_for_org(org_id: str) -> list[SingleMessageEndpoint]:
    return [SingleMessageEndpoint(**item) for item in get_all_items_by_index(SME_TABLE_NAME, "org_id", org_id)]
