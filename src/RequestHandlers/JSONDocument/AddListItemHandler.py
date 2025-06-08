import json
from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from pydantic import BaseModel
from Models import JSONDocument, User

class AddListItemParams(BaseModel):
    path: str
    value: str
    type: str

def add_list_item_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> JSONDocument.JSONDocument:
    body = AddListItemParams(**json.loads(lambda_event.body))
    document_id = lambda_event.requestParameters.get("document_id")
    if not document_id:
        raise Exception("document_id is required", 400)
    
    if user:
        db_user = User.get_user(user.sub)
        return JSONDocument.add_list_item(document_id, body.path, body.value, body.type, db_user)
    else:
        # For public documents when no user is authenticated
        return JSONDocument.add_list_item(document_id, body.path, body.value, body.type, None)
