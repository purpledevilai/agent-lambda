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

def invoke_lambda(lambda_name: str, event: dict, invokation_type: str = "Event"):
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=lambda_name,
        InvocationType=invokation_type,
        Payload=bytes(json.dumps(event), 'utf-8')
    )
    if invokation_type == "RequestResponse":
        return json.loads(response["Payload"].read().decode("utf-8"))