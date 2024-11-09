import uuid
import json
from AWS.CognitoFunctions import get_user_from_cognito
from AWS.APIGatewayFunctions import create_api_gateway_response
from RequestHandlers.AgentMessageHandler import agent_message_handler


# LAMBDA HANDLER - What gets called when a request is made. event has any data that's passed in the request
def lambda_handler(event, context):
    try:

        # Get authentication token
        if "headers" not in event or "Authorization" not in event["headers"]:
            raise Exception("No authentication token provided")
        token = event["headers"]["Authorization"]

        # Get user from cognito
        user = get_user_from_cognito(token)

        # Get the body of the request
        body = json.loads(event["body"])

        # Check for required params
        if "message" not in body:
            raise Exception("No message provided")
        
        # Create context_id if none provided
        if "context_id" not in body or body["context_id"] == "":
            body["context_id"] = str(uuid.uuid4())

        # Check for agent name and set to default if not provided
        if "agent_name" not in body or body["agent_name"] == "":
            body["agent_name"] = "default"
            
        # Get the message and conversation ID
        message = body["message"]
        context_id = body["context_id"]
        agent_name = body["agent_name"]

        response = agent_message_handler(agent_name, message, context_id, user["sub"])

        return create_api_gateway_response(200, response)

    # Return any errors   
    except Exception as e:
        return create_api_gateway_response(400, {
            'error': str(e)
        })
