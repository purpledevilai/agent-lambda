import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from pydantic import BaseModel
from typing import Optional
from Models import JSONDocument, User
from Lib.GraphQLUtils import create_schema, get_value_at_path, schema_to_sdl


class SchemaResponse(BaseModel):
    schema: str


def get_graphql_schema_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> SchemaResponse:
    document_id = lambda_event.requestParameters.get("document_id")
    if not document_id:
        raise Exception("document_id is required", 400)

    path = None
    if lambda_event.queryStringParameters is not None:
        path = lambda_event.queryStringParameters.get("path")

    if user:
        db_user = User.get_user(user.sub)
        document = JSONDocument.get_json_document_for_user(document_id, db_user)
    else:
        document = JSONDocument.get_public_json_document(document_id)

    data = document.data
    sub_data = get_value_at_path(data, path) if path else data

    schema = create_schema(sub_data)
    sdl = schema_to_sdl(schema)
    return SchemaResponse(schema=sdl)
