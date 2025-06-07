from typing import Any, Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from pydantic import BaseModel
from Models import JSONDocument, User

class GetValueResponse(BaseModel):
    value: Any

def get_value_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> GetValueResponse:
    document_id = lambda_event.requestParameters.get("document_id")
    if not document_id:
        raise Exception("document_id is required", 400)
    if not lambda_event.queryStringParameters or "path" not in lambda_event.queryStringParameters:
        raise Exception("path is required", 400)
    path = lambda_event.queryStringParameters["path"]
    db_user = User.get_user(user.sub) if user else None
    value = JSONDocument.get(document_id, path, db_user)
    return GetValueResponse(value=value)
