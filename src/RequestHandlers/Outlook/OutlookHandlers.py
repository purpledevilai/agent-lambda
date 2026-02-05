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

# Microsoft OAuth endpoints (using 'common' for multi-tenant support)
OUTLOOK_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
OUTLOOK_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

# Outlook/Graph API scopes for mail operations
OUTLOOK_SCOPES = [
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/Mail.Read.Shared",
    "https://graph.microsoft.com/Mail.Send.Shared",
    "https://graph.microsoft.com/User.Read",
    "offline_access",
]


class OutlookAuthUrlResponse(BaseModel):
    auth_url: str


class OutlookAuthResponse(BaseModel):
    integration_id: str
    type: str
    email: str


def outlook_auth_url_handler(lambda_event: LambdaEvent, user: CognitoUser) -> OutlookAuthUrlResponse:
    """
    Generate the Outlook OAuth authorization URL.
    
    Query params:
        org_id (optional): The organization ID to associate the integration with
        state (optional): State parameter to pass through OAuth flow
    
    Returns:
        auth_url: The URL to redirect the user to for Outlook authorization
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
        "client_id": os.environ["OUTLOOK_CLIENT_ID"],
        "redirect_uri": os.environ["OUTLOOK_REDIRECT_URI"],
        "response_type": "code",
        "scope": " ".join(OUTLOOK_SCOPES),
        "response_mode": "query",
        "prompt": "consent",  # Force consent to ensure refresh_token
        "state": state,
    }
    
    auth_url = f"{OUTLOOK_AUTH_URL}?{urlencode(params)}"
    return OutlookAuthUrlResponse(auth_url=auth_url)


def outlook_auth_code_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Integration.Integration:
    """
    Exchange the authorization code for tokens and create/update the Outlook integration.
    
    Request body:
        code: The authorization code from Microsoft OAuth
    
    Query params:
        org_id (optional): The organization ID to associate the integration with
    
    Returns:
        The created or updated Outlook integration
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
        "client_id": os.environ["OUTLOOK_CLIENT_ID"],
        "client_secret": os.environ["OUTLOOK_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": os.environ["OUTLOOK_REDIRECT_URI"],
        "scope": " ".join(OUTLOOK_SCOPES),
    }
    
    resp = requests.post(OUTLOOK_TOKEN_URL, data=payload)
    if resp.status_code != 200:
        logger.error(f"Failed to exchange Outlook auth code: {resp.text}")
        raise Exception(f"Failed to exchange Outlook auth code: {resp.text}", resp.status_code)
    
    data = resp.json()
    
    # Get user's email address from the Graph API
    email = _get_user_email(data["access_token"])
    
    integration_config = {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "expires_in": data.get("expires_in"),
        "scope": data.get("scope"),
        "expires_at": int(time.time()) + data.get("expires_in", 0),
        "email": email,
    }
    
    # Check if Outlook integration already exists for this org
    outlook_integration = None
    for integ in Integration.get_integrations_in_org(org_id):
        if integ.type == "outlook":
            # Check if it's the same email account
            if integ.integration_config.get("email") == email:
                outlook_integration = integ
                break
    
    if outlook_integration:
        # Update existing integration
        outlook_integration.integration_config = integration_config
        Integration.save_integration(outlook_integration)
    else:
        # Create new integration
        outlook_integration = Integration.create_integration(
            org_id=org_id,
            type="outlook",
            integration_config=integration_config
        )
    
    return outlook_integration


def _get_user_email(access_token: str) -> str:
    """Get the authenticated user's email address from Microsoft Graph API."""
    resp = requests.get(
        f"{GRAPH_API_BASE}/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if resp.status_code != 200:
        logger.error(f"Failed to get user email: {resp.text}")
        return "unknown"
    
    data = resp.json()
    # Microsoft Graph returns mail or userPrincipalName
    return data.get("mail") or data.get("userPrincipalName", "unknown")

