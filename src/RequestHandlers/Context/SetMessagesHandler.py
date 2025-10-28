import json
from typing import Optional, List
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Context, User
from Models.Context import MessageType


class SetMessagesInput(BaseModel):
    context_id: str
    messages: List[MessageType]


def set_messages_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Context.FilteredContext:
    """
    Replace all messages in an existing context.
    Validates that tool responses have corresponding tool calls.
    Returns the updated filtered context.
    """
    # Get the body of the request
    body = SetMessagesInput(**json.loads(lambda_event.body))
    
    # Get the context
    context = None
    if user:
        context = Context.get_context_for_user(body.context_id, user.sub)
    else:
        context = Context.get_public_context(body.context_id)
    
    # Validate the messages
    Context.validate_messages(body.messages)
    
    # Convert filtered messages to dict messages
    new_dict_messages = Context.filtered_messages_to_dict_messages(body.messages)
    
    # Replace all messages
    context.messages = new_dict_messages
    
    # Save the context
    Context.save_context(context)
    
    # Return the filtered context
    return Context.transform_to_filtered_context(context, show_tool_calls=True)

