from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from pydantic import BaseModel
from typing import Dict, Any

class Schema(BaseModel):
    schema: Dict[str, Any]

def get_schema_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Schema:
    pass
    