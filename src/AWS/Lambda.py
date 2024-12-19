from dataclasses import dataclass
from typing import Optional

@dataclass
class LambdaEvent:
    path: str
    httpMethod: dict
    queryStringParameters: Optional[dict]
    headers: dict
    body: Optional[str]