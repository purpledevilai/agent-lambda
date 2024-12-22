from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Context, SuccessResponse

def delete_context_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse.SuccessResponse:
    context_id = lambda_event.requestParameters.get("context_id")
    if not context_id:
        raise Exception("context_id is required", 400)
    context = Context.get_context_for_user(context_id, user.sub)
    Context.delete_context(context.context_id)
    return SuccessResponse.SuccessResponse(**{
        "success": True
    })
