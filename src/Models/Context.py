import os
from datetime import datetime
import uuid
from AWS.DynamoDB import get_item, put_item, get_all_items_by_index, delete_item
from AWS.CloudWatchLogs import get_logger
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from Models import Agent

logger = get_logger(log_level=os.environ["LOG_LEVEL"])

CONTEXTS_TABLE_NAME = os.environ["CONTEXTS_TABLE_NAME"]
CONTEXTS_PRIMARY_KEY = os.environ["CONTEXTS_PRIMARY_KEY"]

class Context(BaseModel):
    context_id: str
    agent_id: str
    user_id: str
    messages: list[dict]
    created_at: int
    updated_at: int
    prompt_args: Optional[dict] = None

class CreateContextParams(BaseModel):
    agent_id: str
    invoke_agent_message: Optional[bool] = False
    prompt_args: Optional[dict] = None

class FilteredMessage(BaseModel):
    sender: str
    message: str

class ToolCallMessage(BaseModel):
    type: str
    tool_call_id: str
    tool_name: str
    tool_input: Optional[dict] = None

class ToolResponseMessage(BaseModel):
    type: str
    tool_call_id: str
    tool_output: str

MessageType = Union[FilteredMessage, ToolCallMessage, ToolResponseMessage]

class FilteredContext(BaseModel):
    context_id: str
    agent_id: str
    user_id: str
    messages: List[MessageType]
    created_at: int
    updated_at: int

class HistoryContext(BaseModel):
    context_id: str
    user_id: str
    last_message: str
    created_at: int
    updated_at: int
    agent: Agent.HistoryAgent


def context_exists(context_id: str) -> bool:
    return get_item(CONTEXTS_TABLE_NAME, CONTEXTS_PRIMARY_KEY, context_id) != None
    
def create_context(agent_id: str, user_id: Optional[str] = None, prompt_args: Optional[dict] = None) -> Context:
    contextData = {
        CONTEXTS_PRIMARY_KEY: str(uuid.uuid4()),
        "agent_id": agent_id,
        "user_id": user_id if user_id is not None else "public",
        "messages": [],
        "prompt_args": prompt_args,
        "created_at": int(datetime.timestamp(datetime.now())),
        "updated_at": int(datetime.timestamp(datetime.now())),
    }
    context = Context(**contextData)
    put_item(CONTEXTS_TABLE_NAME, contextData)
    return context


def get_context(context_id: str) -> Context:
    item = get_item(CONTEXTS_TABLE_NAME, CONTEXTS_PRIMARY_KEY, context_id)
    if item is None:
        raise Exception(f"Context with id: {context_id} does not exist", 404)
    return Context(**item)
    
def get_context_for_user(context_id: str, user_id: str) -> Context:
    context = get_context(context_id)
    if (context.user_id == "public"):
        return context
    if (context.user_id == user_id):
        return context
    raise Exception(f"Context does not belong to user", 403)

def get_public_context(context_id: str) -> Context:
    context = get_context(context_id)
    if (context.user_id == "public"):
        return context
    raise Exception(f"Context is not public", 403)

def save_context(context: Context) -> None:
    context.updated_at = int(datetime.timestamp(datetime.now()))
    put_item(CONTEXTS_TABLE_NAME, context.model_dump())

def get_contexts_by_user_id(user_id: str) -> list[Context]:
    items = get_all_items_by_index(CONTEXTS_TABLE_NAME, "user_id", user_id)
    contexts = []
    for item in items:
        try:
            contexts.append(Context(**item))
        except Exception as e:
            logger.error(f"Error parsing context: {item}")
    return contexts

def delete_context(context_id: str) -> None:
    delete_item(CONTEXTS_TABLE_NAME, CONTEXTS_PRIMARY_KEY, context_id)

def delete_all_contexts_for_user(user_id: str) -> None:
    contexts = get_contexts_by_user_id(user_id)
    for context in contexts:
        delete_context(context.context_id)

def transform_to_filtered_context(context: Context, show_tool_calls: bool = False) -> FilteredContext:
    messages = []
    for message in context.messages:
        if (message["type"] == "human" or (message["type"] == "ai" and message["content"])):
                messages.append(FilteredMessage(**{
                    "sender": message["type"],
                    "message": message["content"]
                }))
                continue
        if (show_tool_calls):
            if (message["type"] == "ai" and len(message["tool_calls"]) > 0):
                for tool_call in message["tool_calls"]:
                    messages.append(ToolCallMessage(**{
                        "type": "tool_call",
                        "tool_call_id": tool_call["id"],
                        "tool_name": tool_call["name"],
                        "tool_input": tool_call["args"]
                    }))
            if (message["type"] == "tool"):
                messages.append(ToolResponseMessage(**{
                    "type": "tool_response",
                    "tool_call_id": message["tool_call_id"],
                    "tool_output": message["content"]
                }))
                
    filtered_context = FilteredContext(**{
        "context_id": context.context_id,
        "agent_id": context.agent_id,
        "user_id": context.user_id,
        "messages": messages,
        "created_at": context.created_at,
        "updated_at": context.updated_at
    })
    return filtered_context

def transform_to_history_context(context: Context, agent: Agent.Agent) -> HistoryContext:
    return HistoryContext(**{
        "context_id": context.context_id,
        "user_id": context.user_id,
        "last_message": context.messages[-1]["content"] if len(context.messages) > 0 else "",
        "created_at": context.created_at,
        "updated_at": context.updated_at,
        "agent": Agent.transform_to_history_agent(agent)
    })


    

