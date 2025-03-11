import os
from datetime import datetime
import uuid
from AWS.DynamoDB import get_item, put_item, delete_item, get_all_items_by_index
from pydantic import BaseModel
from Models import User
from typing import Optional


TOOLS_TABLE_NAME = os.environ["TOOLS_TABLE_NAME"]
TOOLS_PRIMARY_KEY = os.environ["TOOLS_PRIMARY_KEY"]

class Tool(BaseModel):
    tool_id: str
    org_id: str
    name: str
    description: str
    pd_id: Optional[str] = None # Parameter Definition ID, can have no parameters
    code: str
    created_at: int
    updated_at: int

class CreateToolParams(BaseModel):
    org_id: Optional[str] = None
    name: str
    description: str
    pd_id: Optional[str] = None
    code: str

class UpdateToolParams(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pd_id: Optional[str] = None
    code: Optional[str] = None


def tool_exists(tool_id: str) -> bool:
    return get_item(TOOLS_TABLE_NAME, TOOLS_PRIMARY_KEY, tool_id) != None

def create_tool(
        org_id: str,
        name: str,
        description: str,
        pd_id: Optional[str], # Parameter Definition ID
        code: str
    ) -> Tool:
    tool_id = str(uuid.uuid4())
    created_at = int(datetime.now().timestamp())
    updated_at = created_at
    tool = Tool(
        tool_id=tool_id,
        org_id=org_id,
        name=name,
        description=description,
        pd_id=pd_id,
        code=code,
        created_at=created_at,
        updated_at=updated_at
    )
    put_item(TOOLS_TABLE_NAME, tool.model_dump())
    return tool

def get_tool(tool_id: str) -> Tool:
    item = get_item(TOOLS_TABLE_NAME, TOOLS_PRIMARY_KEY, tool_id)
    if item == None:
        raise Exception(f"Tool {tool_id} not found", 404)
    return Tool(**item)

def get_tool_for_user(tool_id: str, user: User.User) -> Tool:
    tool = get_tool(tool_id)
    if (tool.org_id not in user.organizations):
        raise Exception(f"Tool does not belong to user's orgs", 403)
    return tool

def get_tool_for_org(tool_id: str, org_id: str) -> Tool:
    tool = get_tool(tool_id)
    if tool.org_id != org_id:
        raise Exception(f"Tool {tool_id} not found", 404)
    return tool

def save_tool(tool: Tool) -> Tool:
    tool.updated_at = int(datetime.now().timestamp())
    put_item(TOOLS_TABLE_NAME, tool.model_dump())
    return tool

def delete_tool(tool_id: str) -> None:
    delete_item(TOOLS_TABLE_NAME, TOOLS_PRIMARY_KEY, tool_id)

def get_tools_for_org(org_id: str) -> list[Tool]:
    return [Tool(**item) for item in get_all_items_by_index(TOOLS_TABLE_NAME, "org_id", org_id)]