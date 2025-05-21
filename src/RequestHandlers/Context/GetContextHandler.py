from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Context

def get_context_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Context.FilteredContext: 
    # Get the path parameters
    context_id = lambda_event.requestParameters.get("context_id")

    # Get the query parameters
    query_params = lambda_event.queryStringParameters
    show_tool_calls = False
    if (query_params):
        show_tool_calls = query_params.get("with_tool_calls")

    if ( not context_id):
        raise Exception("context_id is required", 400)
    context = None
    if (user):
        context = Context.get_context_for_user(context_id, user.sub)
    else:
        context = Context.get_public_context(context_id)
    return Context.transform_to_filtered_context(context, show_tool_calls)


    


            