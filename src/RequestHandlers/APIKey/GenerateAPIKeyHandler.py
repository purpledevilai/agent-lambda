import json
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import APIKey, User

AUTHORIZED_EMAIL = "purpledevilai@gmail.com"

class GenerateAPIKeyInput(BaseModel):
    org_id: str

def generate_api_key_handler(lambda_event: LambdaEvent, user: CognitoUser) -> APIKey.APIKey:
    """
    Generate a new API key for the specified organization.
    Only accessible by purpledevilai@gmail.com
    
    POST /generate-api-key
    Body: {"org_id": "..."}
    """
    # Check if user is authorized
    if user.email != AUTHORIZED_EMAIL:
        raise Exception(f"Unauthorized: Only {AUTHORIZED_EMAIL} can generate API keys", 403)
    
    body = GenerateAPIKeyInput(**json.loads(lambda_event.body))
    
    # Verify the user has access to this organization
    db_user = User.get_user(user.sub)
    if body.org_id not in db_user.organizations:
        raise Exception(f"User does not have access to organization {body.org_id}", 403)
    
    # Create the API key
    api_key = APIKey.create_api_key(org_id=body.org_id)
    
    return api_key

