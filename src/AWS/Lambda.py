from pydantic import BaseModel
from typing import Optional

class LambdaEvent(BaseModel):
    path: str
    httpMethod: str
    queryStringParameters: Optional[dict] = None
    requestParameters: Optional[dict] = {}
    headers: Optional[dict] = {}
    body: Optional[str] = None