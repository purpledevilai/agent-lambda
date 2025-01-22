import json
from pydantic import BaseModel
from typing import Optional
import boto3

class LambdaEvent(BaseModel):
    path: str
    httpMethod: str
    queryStringParameters: Optional[dict] = None
    requestParameters: Optional[dict] = {}
    headers: Optional[dict] = {}
    body: Optional[str] = None

def invoke_lambda(lambda_name: str, event: dict) -> None:
    client = boto3.client('lambda')
    client.invoke(
        FunctionName=lambda_name,
        InvocationType="Event",  # Asynchronous invocation
        Payload=bytes(json.dumps(event), 'utf-8')
        
    )