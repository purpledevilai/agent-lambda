import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel
from AWS.DynamoDB import get_item, get_all_items_by_index, get_items_by_scan, put_item, delete_item
from AWS.CloudWatchLogs import get_logger
from Models import User

logger = get_logger(log_level=os.environ["LOG_LEVEL"])

DOCUMENTS_TABLE_NAME = os.environ["JSON_DOCUMENTS_TABLE_NAME"]
DOCUMENTS_PRIMARY_KEY = os.environ["JSON_DOCUMENTS_PRIMARY_KEY"]  # likely "document_id"

# --------------------- Models ---------------------

class JSONDocument(BaseModel):
    document_id: str
    data: Dict[str, Any]
    org_id: str
    created_at: int
    updated_at: int
    is_public: bool = False

class CreateJSONDocumentParams(BaseModel):
    data: Dict[str, Any]
    org_id: Optional[str] = None
    is_public: Optional[bool] = False

class UpdateJSONDocumentParams(BaseModel):
    data: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None

# --------------------- CRUD Functions ---------------------

def json_document_exists(document_id: str) -> bool:
    return get_item(DOCUMENTS_TABLE_NAME, DOCUMENTS_PRIMARY_KEY, document_id) is not None

def create_json_document(params: CreateJSONDocumentParams) -> JSONDocument:
    if params.org_id is None:
        raise Exception("Organization ID must be provided", 400)
    now = int(datetime.timestamp(datetime.now()))
    document_data = {
        DOCUMENTS_PRIMARY_KEY: str(uuid.uuid4()),
        "data": params.data,
        "org_id": params.org_id,
        "is_public": params.is_public,
        "created_at": now,
        "updated_at": now
    }
    document = JSONDocument(**document_data)
    put_item(DOCUMENTS_TABLE_NAME, document_data)
    return document

def get_json_document(document_id: str) -> JSONDocument:
    item = get_item(DOCUMENTS_TABLE_NAME, DOCUMENTS_PRIMARY_KEY, document_id)
    if item is None:
        raise Exception(f"JSONDocument with id: {document_id} does not exist", 404)
    return JSONDocument(**item)

def get_public_json_document(document_id: str) -> JSONDocument:
    document = get_json_document(document_id)
    if document.is_public:
        return document
    raise Exception(f"Document is not public", 403)

def save_json_document(document: JSONDocument) -> None:
    document.updated_at = int(datetime.timestamp(datetime.now()))
    put_item(DOCUMENTS_TABLE_NAME, document.model_dump())

def delete_json_document(document_id: str) -> None:
    delete_item(DOCUMENTS_TABLE_NAME, DOCUMENTS_PRIMARY_KEY, document_id)

def get_json_document_for_user(document_id: str, user: User.User) -> JSONDocument:
    doc = get_json_document(document_id)
    if doc.is_public:
        return doc
    if doc.org_id in user.organizations:
        return doc
    raise Exception(f"Document does not belong to user's orgs", 403)

def parse_json_document_items(items: list[dict]) -> list[JSONDocument]:
    documents = []
    for item in items:
        try:
            documents.append(JSONDocument(**item))
        except Exception as e:
            logger.error(f"Error parsing document: {e}")
    return documents

def get_json_documents_from_ids(document_ids: list[str]) -> list[JSONDocument]:
    items = get_items_by_scan(DOCUMENTS_TABLE_NAME, DOCUMENTS_PRIMARY_KEY, document_ids)
    return parse_json_document_items(items)

def get_json_documents_in_org(org_id: str) -> list[JSONDocument]:
    items = get_all_items_by_index(DOCUMENTS_TABLE_NAME, "org_id", org_id)
    return parse_json_document_items(items)

def delete_json_documents_in_org(org_id: str) -> None:
    documents = get_json_documents_in_org(org_id)
    for doc in documents:
        delete_json_document(doc.document_id)
