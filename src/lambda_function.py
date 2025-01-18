import os
import json
import re
from typing import Optional
from pydantic import BaseModel
from AWS.Lambda import LambdaEvent
from AWS.Cognito import get_user_from_cognito, CognitoUser
from AWS.APIGateway import create_api_gateway_response, APIGatewayResponse
from AWS.CloudWatchLogs import get_logger

# User
from RequestHandlers.User.CreateUserHandler import create_user_handler
from RequestHandlers.User.GetUserHandler import get_user_handler
from RequestHandlers.User.DeleteUserHandler import delete_user_handler

# Organization
from RequestHandlers.Organization.CreateOrganizationHandler import create_organization_handler

# Context
from RequestHandlers.Context.CreateContextHandler import create_context_handler
from RequestHandlers.Context.GetContextHandler import get_context_handler
from RequestHandlers.Context.DeleteContextHandler import delete_context_handler
from RequestHandlers.Context.GetContextHistoryHandler import get_context_history_handler

# Agents
from RequestHandlers.Agent.GetAgentsHandler import get_agents_handler
from RequestHandlers.Agent.CreateAgentHandler import create_agent_handler
from RequestHandlers.Agent.GetAgentHandler import get_agent_handler
from RequestHandlers.Agent.UpdateAgentHandler import update_agent_handler
from RequestHandlers.Agent.DeleteAgentHandler import delete_agent_handler

# Chat
from RequestHandlers.Chat.ChatHandler import chat_handler

# Chatpage
from RequestHandlers.ChatPage.CreateChatPageHandler import create_chat_page_handler
from RequestHandlers.ChatPage.GetChatPageHandler import get_chat_page_handler
from RequestHandlers.ChatPage.UpdateChatPageHandler import update_chat_page_handler
from RequestHandlers.ChatPage.DeleteChatPageHandler import delete_chat_page_handler
from RequestHandlers.ChatPage.GetChatPagesHandler import get_chat_pages_handler

# Scrape Page
from RequestHandlers.ScrapePage.ScrapePageHandler import scrape_page_handler

# Set up the logger
logger = get_logger(log_level=os.environ["LOG_LEVEL"])

# Handler registry
handler_registry = {
    "/user": {
        "POST": {
            "handler": create_user_handler,
            "public": False
        },
        "GET": {
            "handler": get_user_handler,
            "public": False
        },
        "DELETE": {
            "handler": delete_user_handler,
            "public": False
        }
    },
    "/organization": {
        "POST": {
            "handler": create_organization_handler,
            "public": False
        }
    },
    "/context": {
        "POST": {
            "handler": create_context_handler,
            "public": True
        }
    },
    "/context/{context_id}": {
        "GET": {
            "handler": get_context_handler,
            "public": True
        },
        "DELETE": {
            "handler": delete_context_handler,
            "public": False
        }
    },
    "/context-history": {
        "GET": {
            "handler": get_context_history_handler,
            "public": False
        }
    },
    "/agents": {
        "GET": {
            "handler": get_agents_handler,
            "public": False
        }
    },
    "/agent": {
        "POST": {
            "handler": create_agent_handler,
            "public": False
        }
    },
    "/agent/{agent_id}": {
        "GET": {
            "handler": get_agent_handler,
            "public": True
        },
        "POST": {
            "handler": update_agent_handler,
            "public": False
        },
        "DELETE": {
            "handler": delete_agent_handler,
            "public": False
        }
    },
    "/chat": {
        "POST": {
            "handler": chat_handler,
            "public": True
        }
    },
    "/chat-page": {
        "POST": {
            "handler": create_chat_page_handler,
            "public": False
        }
    },
    "/chat-page/{chat_page_id}": {
        "POST": {
            "handler": update_chat_page_handler,
            "public": False
        },
        "GET": {
            "handler": get_chat_page_handler,
            "public": True
        },
        "DELETE": {
            "handler": delete_chat_page_handler,
            "public": False
        }
    },
    "/chat-pages": {
        "GET": {
            "handler": get_chat_pages_handler,
            "public": False
        }
    },
    "/scrape-page/{link}": {
        "GET": {
            "handler": scrape_page_handler,
            "public": False
        }
    }
}

def match_route(request_path: str, method: str, handler_registry: dict) -> tuple:
    for route, methods in handler_registry.items():
        # Replace placeholder variables with regex capture groups
        route_pattern = re.sub(
            r'\{(\w+)\}', 
            lambda m: rf'(?P<{m.group(1)}>.+)' if m.group(1) == 'link' else rf'(?P<{m.group(1)}>[^/]+)', 
            route
        )
        route_regex = f"^{route_pattern}$"
        match = re.match(route_regex, request_path)
        
        if match:
            handler_info = methods.get(method)
            if handler_info:
                # Extract named groups as parameters
                params = match.groupdict()
                handler = handler_info.get('handler')
                is_public = handler_info.get('public', False)  # Default to False if 'public' key is missing
                return handler, params, is_public
    
    return None, None, None


# LAMBDA HANDLER - What gets called when a request is made. event has any data that's passed in the request
def lambda_handler(event: dict, context) -> APIGatewayResponse:
    logger.info("Received event: " + json.dumps(event, indent=2))

    # Create a LambdaEvent object from the event
    lambda_event = LambdaEvent(**event)

    try:
        # Get the request details
        request_path: str = lambda_event.path
        request_method: str = lambda_event.httpMethod

        # Get the handler for the request
        handler, request_params, is_public = match_route(request_path, request_method, handler_registry)
        if not handler:
            raise Exception("Invalid request path", 404)
        lambda_event.requestParameters = request_params

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
            if not is_public:
                raise Exception("Not authenticated", 401)
            
        # Call the handler
        response: BaseModel = handler(
            lambda_event=lambda_event,
            user=user
        )

        # Return the response 
        return create_api_gateway_response(200, response.model_dump())
            

    # Return any errors   
    except Exception as e:
        logger.error(str(e))
        error, code = e.args if len(e.args) == 2 else (e, 500)
        return create_api_gateway_response(code, {
            'error': str(error)
        })
