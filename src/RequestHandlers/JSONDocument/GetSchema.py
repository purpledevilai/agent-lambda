from typing import Dict, Any, Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from pydantic import BaseModel
from Models import JSONDocument, User

class Schema(BaseModel):
    schema: Dict[str, Any]

def get_schema_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Schema:
    document_id = lambda_event.requestParameters.get("document_id")
    if not document_id:
        raise Exception("document_id is required", 400)
    db_user = User.get_user(user.sub) if user else None
    schema = JSONDocument.get_shape(document_id, db_user)
    return Schema(schema=schema)
