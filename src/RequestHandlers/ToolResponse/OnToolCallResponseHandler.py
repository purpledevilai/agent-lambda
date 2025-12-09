import json
import requests
from typing import Optional
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from AWS.CloudWatchLogs import get_logger
from Models import Agent, User, Context, Organization
import os

logger = get_logger(log_level=os.environ["LOG_LEVEL"])


class OnToolCallResponseInput(BaseModel):
    context_id: str
    tool_call_id: str
    response: str


class OnToolCallResponseOutput(BaseModel):
    success: bool
    message: str


def on_tool_call_response_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> OnToolCallResponseOutput:
    """
    Handle async tool call responses from external systems.
    Adds the response to the context's async_tool_response_queue and triggers webhooks if configured.
    """
    # Get the body of the request
    body = OnToolCallResponseInput(**json.loads(lambda_event.body))
    
    # Get the context
    context = None
    if user:
        db_user = User.get_user(user.sub)
        context = Context.get_context_for_user(body.context_id, db_user.user_id)
    else:
        context = Context.get_public_context(body.context_id)
    
    # Verify the user has access to the org the context belongs to
    agent = Agent.get_agent(context.agent_id)
    
    if user:
        db_user = User.get_user(user.sub)
        if agent.org_id not in db_user.organizations:
            raise Exception(f"User does not have access to organization {agent.org_id}", 403)
    else:
        # Public contexts should have public agents
        if not agent.is_public:
            raise Exception("Cannot access non-public agent's context", 403)
    
    # Add the async tool response to the queue
    context = Context.add_async_tool_response(context, body.tool_call_id, body.response)
    
    # Get the organization and check for webhook
    organization = Organization.get_organization(agent.org_id)
    
    if organization.webhook_url:
        # Send webhook notification (fire and forget)
        try:
            webhook_payload = {
                "event_name": "async_tool_response_received",
                "payload": {
                    "context_id": body.context_id,
                    "tool_call_id": body.tool_call_id
                }
            }
            requests.post(
                organization.webhook_url,
                json=webhook_payload,
                timeout=5
            )
            logger.info(f"Webhook sent to {organization.webhook_url} for context {body.context_id}")
        except Exception as e:
            # Log and continue silently if webhook fails
            logger.error(f"Failed to send webhook to {organization.webhook_url}: {e}")
    
    return OnToolCallResponseOutput(
        success=True,
        message="Async tool response added to queue"
    )

