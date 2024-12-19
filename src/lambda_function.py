import os
import json
from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import get_user_from_cognito, CognitoUser
from AWS.APIGateway import create_api_gateway_response, APIGatewayResponse
from AWS.CloudWatchLogs import get_logger
from RequestHandlers.ChatHandler import chat_handler
from RequestHandlers.GetChatHistoryHandler import get_chat_history_handler
from RequestHandlers.GetContextHandler import get_context_handler
from RequestHandlers.GetAgentsHandler import get_agents_handler
from RequestHandlers.CreateOrganizationHandler import create_organization_handler
from src.RequestHandlers.User.CreateUserHandler import create_user_handler
from RequestHandlers.CreateOrUpdateAgentHandler import create_or_update_agent_handler
from src.RequestHandlers.User.GetUserHandler import get_user_handler
from RequestHandlers.GetContextHistoryHandler import get_context_history
from RequestHandlers.DeleteContextHandler import delete_context_handler
from pydantic import BaseModel

logger = get_logger(log_level=os.environ["LOG_LEVEL"])

public_endpoints = [("GET", "/context"), ("POST", "/chat")]

handler_registry = {
    "/user": {
        "POST": create_user_handler,
        "GET": get_user_handler
    },
    "/orgainization": {
        "POST": create_organization_handler
    },
    "/context": {
        "GET": get_context_handler,
        "DELETE": delete_context_handler
    },
    "/context-history": {
        "GET": get_context_history
    },
    "/agents": {
        "GET": get_agents_handler
    },
    "/agent": {
        "POST": create_or_update_agent_handler
    },
    "/chat": {
        "POST": chat_handler
    }
}


# LAMBDA HANDLER - What gets called when a request is made. event has any data that's passed in the request
def lambda_handler(event: dict, context) -> APIGatewayResponse:
    logger.info("Received event: " + json.dumps(event, indent=2))

    # Create a LambdaEvent object from the event
    lambda_event = LambdaEvent(**event)

    try:
        # Get the request details
        request_path: str = lambda_event.path
        request_method: str = lambda_event.httpMethod

        # Get the user, if any, from the token
        user: Optional[CognitoUser] = None
        try:
            if "Authorization" not in lambda_event.headers:
                raise Exception("No authentication token provided")
            token = lambda_event.headers["Authorization"]
            user = get_user_from_cognito(token)
        except Exception as e:
            logger.error(str(e))
            # No user, but request is to a public endpoint
            if (request_method, request_path) not in public_endpoints:
                raise Exception("Not authenticated", 401)
            
        # Path exists
        if request_path not in handler_registry:
            raise Exception("Invalid request path")
        
        # Method exists
        if request_method not in handler_registry[request_path]:
            raise Exception("Invalid request method")
        
        # Call the handler
        response: BaseModel = handler_registry[request_path][request_method](
            lambda_event=lambda_event,
            user=user
        )

        # Return the response 
        return create_api_gateway_response(200, response.model_dump())
            
            
        # # POST /user - Create a new user
        # if request_method == "POST" and request_path == "/user":
        #     response = create_user_handler(user_id)

        # # GET /user - Get the user
        # if request_method == "GET" and request_path == "/user":
        #     print(json.dumps(user, indent=4))
        #     response = get_user_handler(user)

        # # POST: /orgainization - Create a new organization
        # if request_method == "POST" and request_path == "/organization":
        #     # Get the body of the request
        #     body = json.loads(event["body"])

        #     # Check for required params
        #     if "name" not in body:
        #         raise Exception("No name provided")
            
        #     # Create the organization
        #     response = create_organization_handler(body["name"], user_id)

        # # GET: /chat-history
        # if request_method == "GET" and request_path == "/chat-history":
        #     response = get_chat_history_handler(user_id)

        # # GET: /context
        # if request_method == "GET" and request_path == "/context":
        #     params = {
        #         "context_id": request_params.get("context_id"),
        #         "agent_id": request_params.get("agent_id"),
        #         "invoke_agent_message": request_params.get("invoke_agent_message", "False").lower() == "true",
        #         "user_id": user_id
        #     }
        #     response = get_context_handler(**params)

        # # DELETE: /context
        # if request_method == "DELETE" and request_path == "/context":
        #     params = {
        #         "context_id": request_params.get("context_id"),
        #         "user_id": user_id
        #     }
        #     response = delete_context_handler(**params)

        # # GET: /context-history
        # if request_method == "GET" and request_path == "/context-history":
        #     response = get_context_history(user_id)

        # # GET: /agents
        # if request_method == "GET" and request_path == "/agents":
        #     org_id = request_params.get("org_id")
        #     response = get_agents_handler(user_id, org_id)

        # if request_method == "POST" and request_path == "/agent":
        #     # Get the body of the request
        #     body = json.loads(event["body"])

        #     params = {
        #         "user_id": user_id,
        #         "org_id": body.get("org_id"),
        #         "agent_id": body.get("agent_id"),
        #         "prompt": body.get("prompt"),
        #         "is_public": body.get("is_public", False),
        #         "agent_name": body.get("agent_name"),
        #         "agent_description": body.get("agent_description")
        #     }
        #     response = create_or_update_agent_handler(**params)
        
        # # CHAT: /chat
        # if request_method == "POST" and request_path == "/chat":
        #     # Get the body of the request
        #     body = json.loads(event["body"])

        #     # Check for required params
        #     if "message" not in body:
        #         raise Exception("No message provided")
            
        #     # Create context_id if none provided
        #     if "context_id" not in body:
        #         raise Exception("No context_id provided")
                
        #     # Get the message and conversation ID
        #     message = body["message"]
        #     context_id = body["context_id"]

        #     response = chat_handler(message, context_id, user_id)


        # # NOT SUPPORTED
        # if (response == None):
        #     raise Exception("Invalid request path")
        
        # return create_api_gateway_response(200, response)

    # Return any errors   
    except Exception as e:
        logger.error(str(e))
        error, code = e.args if len(e.args) == 2 else (e, 500)
        return create_api_gateway_response(code, {
            'error': str(error)
        })
