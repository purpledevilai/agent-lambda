import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from pydantic import BaseModel
from typing import Optional, Any
from Models import JSONDocument, User
from Lib.GraphQLUtils import create_schema, execute_query, set_value_at_path


class GraphQLRequest(BaseModel):
    query: str


class GraphQLResponse(BaseModel):
    data: Optional[dict] = None
    errors: Optional[list[str]] = None


def graphql_query_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> GraphQLResponse:
    document_id = lambda_event.requestParameters.get("document_id")
    if not document_id:
        raise Exception("document_id is required", 400)

    body = GraphQLRequest(**json.loads(lambda_event.body))

    if user:
        db_user = User.get_user(user.sub)
        document = JSONDocument.get_json_document_for_user(document_id, db_user)
    else:
        document = JSONDocument.get_public_json_document(document_id)

    data = document.data

    def update_resolver(path=None, value=None):
        if user is None:
            raise Exception("Not authenticated", 401)
        parsed_value = json.loads(value) if value is not None else None
        set_value_at_path(data, path or "", parsed_value)
        document.data = data
        JSONDocument.save_json_document(document)
        return data

    schema = create_schema(data, update_resolver)
    result = execute_query(schema, body.query, data)

    if result.errors:
        return GraphQLResponse(data=result.data, errors=[str(e) for e in result.errors])

    return GraphQLResponse(data=result.data)
