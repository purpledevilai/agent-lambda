import json
from AWS.Lambda import LambdaEvent, invoke_lambda
from AWS.Cognito import CognitoUser
from pydantic import BaseModel


class TestToolParams(BaseModel):
    function_name: str
    code: str
    params: dict

class TestToolResponse(BaseModel):
    result: str


def test_tool_handler(lambda_event: LambdaEvent, user: CognitoUser) -> TestToolResponse:

    # Get the body of the request
    body = TestToolParams(**json.loads(lambda_event.body))

    response = invoke_lambda(
        lambda_name="execution-lambda",
        event={
            "function_name": body.function_name,
            "code": body.code,
            "params": body.params
        },
        invokation_type="RequestResponse"
    )

    return TestToolResponse(**response)
