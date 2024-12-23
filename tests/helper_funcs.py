from typing import Optional, TypedDict
import json

class Request(TypedDict):
    path: str
    httpMethod: str
    queryStringParameters: Optional[dict]
    headers: dict
    body: Optional[str]

def create_request(
        method: str, 
        path: str,
        headers: Optional[dict] = {},
        body: Optional[dict] = None, 
        query_string_parameters: Optional[dict] = {}, 
    ) -> Request:
    return {
        "httpMethod": method,
        "path": path,
        "body": json.dumps(body) if body else None,
        "queryStringParameters": query_string_parameters,
        "headers": headers
    }