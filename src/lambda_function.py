import os
import json
from AWS.CognitoFunctions import get_user_from_cognito
from AWS.APIGatewayFunctions import create_api_gateway_response
from AWS.CloudWatchLogsFunctions import get_logger
from RequestHandlers.AgentMessageHandler import agent_message_handler
from RequestHandlers.GetChatHistoryHandler import get_chat_history_handler
from RequestHandlers.GetContextHandler import get_context_handler


# LAMBDA HANDLER - What gets called when a request is made. event has any data that's passed in the request
def lambda_handler(event, context):

    logger = get_logger(log_level=os.environ["LOG_LEVEL"])
    logger.info("Received event: " + json.dumps(event, indent=2))

    try:

        request_method = event["httpMethod"]
        request_path = event["path"]
        request_params = event.get("queryStringParameters") if event.get("queryStringParameters") is not None else {}
        response = None

        # Get authentication token
        if "headers" not in event or "Authorization" not in event["headers"]:
            raise Exception("No authentication token provided")
        token = event["headers"]["Authorization"]

        # Get user from cognito
        user = get_user_from_cognito(token)


        # POST: /chat-history
        if request_method == "GET" and request_path == "/chat-history":
            response = get_chat_history_handler(user["sub"])

         # GET: /context
        if request_method == "GET" and request_path == "/context":
            context_id = request_params.get("context_id")
            agent_id = request_params.get("agent_id")
            response = get_context_handler(context_id, agent_id, user["sub"])
        
        # GET: /chat
        if request_method == "POST" and request_path == "/chat":
            # Get the body of the request
            body = json.loads(event["body"])

            # Check for required params
            if "message" not in body:
                raise Exception("No message provided")
            
            # Create context_id if none provided
            if "context_id" not in body:
                raise Exception("No context_id provided")
                
            # Get the message and conversation ID
            message = body["message"]
            context_id = body["context_id"]

            response = agent_message_handler(message, context_id, user["sub"])


        # NOT SUPPORTED
        if (response == None):
            raise Exception("Invalid request path")
        
        return create_api_gateway_response(200, response)

    # Return any errors   
    except Exception as e:
        logger.error(str(e))
        return create_api_gateway_response(400, {
            'error': str(e)
        })
