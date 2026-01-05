import json
import os
import time
import requests
from urllib.parse import urlencode
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from AWS.CloudWatchLogs import get_logger
from Models import Integration, User

logger = get_logger(log_level=os.environ.get("LOG_LEVEL", "INFO"))

GMAIL_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GMAIL_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Gmail scopes for read, send, and modify (mark read/unread)
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailAuthUrlResponse(BaseModel):
    auth_url: str


class GmailAuthResponse(BaseModel):
    integration_id: str
    type: str
    email: str


def gmail_auth_url_handler(lambda_event: LambdaEvent, user: CognitoUser) -> GmailAuthUrlResponse:
    """
    Generate the Gmail OAuth authorization URL.
    
    Query params:
        org_id (optional): The organization ID to associate the integration with
        state (optional): State parameter to pass through OAuth flow
    
    Returns:
        auth_url: The URL to redirect the user to for Gmail authorization
    """
    db_user = User.get_user(user.sub)
    if len(db_user.organizations) == 0:
        raise Exception("User is not a member of any organizations", 400)
    
    # Get org_id from query params or use first org
    org_id = None
    if lambda_event.queryStringParameters:
        org_id = lambda_event.queryStringParameters.get("org_id")
    if not org_id:
        org_id = db_user.organizations[0]
    if org_id not in db_user.organizations:
        raise Exception("User is not a member of the specified organization", 403)
    
    # Get optional state parameter
    state = org_id  # Default state to org_id
    if lambda_event.queryStringParameters and lambda_event.queryStringParameters.get("state"):
        state = lambda_event.queryStringParameters.get("state")
    
    params = {
        "client_id": os.environ["GMAIL_CLIENT_ID"],
        "redirect_uri": os.environ["GMAIL_REDIRECT_URI"],
        "response_type": "code",
        "scope": " ".join(GMAIL_SCOPES),
        "access_type": "offline",  # Required to get refresh_token
        "prompt": "consent",  # Force consent to ensure refresh_token
        "state": state,
    }
    
    auth_url = f"{GMAIL_AUTH_URL}?{urlencode(params)}"
    return GmailAuthUrlResponse(auth_url=auth_url)


def gmail_auth_code_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Integration.Integration:
    """
    Exchange the authorization code for tokens and create/update the Gmail integration.
    
    Request body:
        code: The authorization code from Google OAuth
    
    Query params:
        org_id (optional): The organization ID to associate the integration with
    
    Returns:
        The created or updated Gmail integration
    """
    body = json.loads(lambda_event.body)
    code = body.get("code")
    if not code:
        raise Exception("code is required", 400)
    
    db_user = User.get_user(user.sub)
    if len(db_user.organizations) == 0:
        raise Exception("User is not a member of any organizations", 400)
    
    # Get org_id from query params or use first org
    org_id = None
    if lambda_event.queryStringParameters:
        org_id = lambda_event.queryStringParameters.get("org_id")
    if not org_id:
        org_id = db_user.organizations[0]
    if org_id not in db_user.organizations:
        raise Exception("User is not a member of the specified organization", 403)
    
    # Exchange code for tokens
    payload = {
        "grant_type": "authorization_code",
        "client_id": os.environ["GMAIL_CLIENT_ID"],
        "client_secret": os.environ["GMAIL_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": os.environ["GMAIL_REDIRECT_URI"],
    }
    
    resp = requests.post(GMAIL_TOKEN_URL, data=payload)
    if resp.status_code != 200:
        logger.error(f"Failed to exchange Gmail auth code: {resp.text}")
        raise Exception(f"Failed to exchange Gmail auth code: {resp.text}", resp.status_code)
    
    data = resp.json()
    
    # Get user's email address from the API
    email = _get_user_email(data["access_token"])
    
    integration_config = {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "expires_in": data.get("expires_in"),
        "scope": data.get("scope"),
        "expires_at": int(time.time()) + data.get("expires_in", 0),
        "email": email,
    }
    
    # Check if Gmail integration already exists for this org
    gmail_integration = None
    for integ in Integration.get_integrations_in_org(org_id):
        if integ.type == "gmail":
            # Check if it's the same email account
            if integ.integration_config.get("email") == email:
                gmail_integration = integ
                break
    
    if gmail_integration:
        # Update existing integration
        gmail_integration.integration_config = integration_config
        Integration.save_integration(gmail_integration)
    else:
        # Create new integration
        gmail_integration = Integration.create_integration(
            org_id=org_id,
            type="gmail",
            integration_config=integration_config
        )
    
    return gmail_integration


def _get_user_email(access_token: str) -> str:
    """Get the authenticated user's email address."""
    resp = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if resp.status_code != 200:
        logger.error(f"Failed to get user email: {resp.text}")
        return "unknown"
    
    data = resp.json()
    return data.get("emailAddress", "unknown")

