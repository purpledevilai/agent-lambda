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

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Google Calendar scopes for event CRUD and calendar viewing
GOOGLE_CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]


class GoogleCalendarAuthUrlResponse(BaseModel):
    auth_url: str


class GoogleCalendarAuthResponse(BaseModel):
    integration_id: str
    type: str
    email: str


def google_calendar_auth_url_handler(lambda_event: LambdaEvent, user: CognitoUser) -> GoogleCalendarAuthUrlResponse:
    """
    Generate the Google Calendar OAuth authorization URL.
    
    Query params:
        org_id (optional): The organization ID to associate the integration with
        state (optional): State parameter to pass through OAuth flow
    
    Returns:
        auth_url: The URL to redirect the user to for Google Calendar authorization
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
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "redirect_uri": os.environ["GOOGLE_CALENDAR_REDIRECT_URI"],
        "response_type": "code",
        "scope": " ".join(GOOGLE_CALENDAR_SCOPES),
        "access_type": "offline",  # Required to get refresh_token
        "prompt": "consent",  # Force consent to ensure refresh_token
        "state": state,
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return GoogleCalendarAuthUrlResponse(auth_url=auth_url)


def google_calendar_auth_code_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Integration.Integration:
    """
    Exchange the authorization code for tokens and create/update the Google Calendar integration.
    
    Request body:
        code: The authorization code from Google OAuth
    
    Query params:
        org_id (optional): The organization ID to associate the integration with
    
    Returns:
        The created or updated Google Calendar integration
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
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": os.environ["GOOGLE_CALENDAR_REDIRECT_URI"],
    }
    
    resp = requests.post(GOOGLE_TOKEN_URL, data=payload)
    if resp.status_code != 200:
        logger.error(f"Failed to exchange Google Calendar auth code: {resp.text}")
        raise Exception(f"Failed to exchange Google Calendar auth code: {resp.text}", resp.status_code)
    
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
    
    # Check if Google Calendar integration already exists for this org
    calendar_integration = None
    for integ in Integration.get_integrations_in_org(org_id):
        if integ.type == "google_calendar":
            # Check if it's the same email account
            if integ.integration_config.get("email") == email:
                calendar_integration = integ
                break
    
    if calendar_integration:
        # Update existing integration
        calendar_integration.integration_config = integration_config
        Integration.save_integration(calendar_integration)
    else:
        # Create new integration
        calendar_integration = Integration.create_integration(
            org_id=org_id,
            type="google_calendar",
            integration_config=integration_config
        )
    
    return calendar_integration


def _get_user_email(access_token: str) -> str:
    """Get the authenticated user's email address using the Calendar API."""
    # First try to get from calendar settings
    resp = requests.get(
        "https://www.googleapis.com/calendar/v3/calendars/primary",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if resp.status_code == 200:
        data = resp.json()
        email = data.get("id")  # Primary calendar ID is the user's email
        if email and "@" in email:
            return email
    
    # Fallback: try userinfo endpoint
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if resp.status_code == 200:
        data = resp.json()
        return data.get("email", "unknown")
    
    logger.error(f"Failed to get user email: {resp.text}")
    return "unknown"

