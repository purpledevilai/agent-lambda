import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from pydantic import BaseModel
from typing import Optional, Any
from Models import JSONDocument, User
from Lib.GraphQLUtils import set_value_at_path


class MutateRequest(BaseModel):
    path: str
    value: Any


def mutate_json_document_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> JSONDocument.JSONDocument:
    if user is None:
        raise Exception("Not authenticated", 401)

    document_id = lambda_event.requestParameters.get("document_id")
    if not document_id:
        raise Exception("document_id is required", 400)

    body = MutateRequest(**json.loads(lambda_event.body))

    db_user = User.get_user(user.sub)
    document = JSONDocument.get_json_document_for_user(document_id, db_user)

    document.data = set_value_at_path(document.data, body.path, body.value)
    JSONDocument.save_json_document(document)

    return document
