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

# Chat Bot
from RequestHandlers.ChatBot.GetChatBotHandler import get_chat_bot_handler

# Scrape Page
from RequestHandlers.ScrapePage.ScrapePageHandler import scrape_page_handler

# Job
from RequestHandlers.Job.GetJobHandler import get_job_handler

# Create Team
from RequestHandlers.CreateTeam.CreateTeamHandler import create_team_handler

# Parameter Definition
from RequestHandlers.ParameterDefinition.CreateParameterDefinitionHandler import create_parameter_definition_handler
from RequestHandlers.ParameterDefinition.GetParameterDefinitionHandler import get_parameter_definition_handler
from RequestHandlers.ParameterDefinition.UpdateParameterDefinitionHandler import update_parameter_definition_handler
from RequestHandlers.ParameterDefinition.DeleteParameterDefinitionHandler import delete_parameter_definition_handler
from RequestHandlers.ParameterDefinition.GetParameterDefinitionsHandler import get_parameter_definitions_handler

# Tool
from RequestHandlers.Tool.CreateToolHandler import create_tool_handler
from RequestHandlers.Tool.GetToolHandler import get_tool_handler
from RequestHandlers.Tool.UpdateToolHandler import update_tool_handler
from RequestHandlers.Tool.DeleteToolHandler import delete_tool_handler
from RequestHandlers.Tool.GetToolsHandler import get_tools_handler
from RequestHandlers.Tool.TestToolHandler import test_tool_handler

# Structured Response Endpoint
from RequestHandlers.StructuredResponseEndpoint.CreateSREHandler import create_sre_handler
from RequestHandlers.StructuredResponseEndpoint.GetSREHandler import get_sre_handler
from RequestHandlers.StructuredResponseEndpoint.UpdateSREHandler import update_sre_handler
from RequestHandlers.StructuredResponseEndpoint.DeleteSREHandler import delete_sre_handler
from RequestHandlers.StructuredResponseEndpoint.GetSREsHandler import get_sres_handler
from RequestHandlers.StructuredResponseEndpoint.RunSREHandler import run_sre_handler

# JSON Documents
from RequestHandlers.JSONDocument.CreateJSONDocumentHandler import create_json_document_handler
from RequestHandlers.JSONDocument.GetJSONDocumentHandler import get_json_document_handler
from RequestHandlers.JSONDocument.UpdateJSONDocumentHandler import update_json_document_handler
from RequestHandlers.JSONDocument.DeleteJSONDocumentHandler import delete_json_document_handler
from RequestHandlers.JSONDocument.GetJSONDocumentsHandler import get_json_documents_handler




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
    },
    "/job/{job_id}": {
        "GET": {
            "handler": get_job_handler,
            "public": False
        }
    },
    "/create-team": {
        "POST": {
            "handler": create_team_handler,
            "public": False
        }
    },
    "/chat-bot/{chat_page_id}": {
        "GET": {
            "handler": get_chat_bot_handler,
            "public": True,
            "return_type": "application/javascript"
        }
    },
    "/parameter-definition": {
        "POST": {
            "handler": create_parameter_definition_handler,
            "public": False
        }
    },
    "/parameter-definition/{pd_id}": {
        "GET": {
            "handler": get_parameter_definition_handler,
            "public": False
        },
        "POST": {
            "handler": update_parameter_definition_handler,
            "public": False
        },
        "DELETE": {
            "handler": delete_parameter_definition_handler,
            "public": False
        }
    },
    "/parameter-definitions": {
        "GET": {
            "handler": get_parameter_definitions_handler,
            "public": False
        }
    },
    "/tool": {
        "POST": {
            "handler": create_tool_handler,
            "public": False
        }
    },
    "/tool/{tool_id}": {
        "GET": {
            "handler": get_tool_handler,
            "public": False
        },
        "POST": {
            "handler": update_tool_handler,
            "public": False
        },
        "DELETE": {
            "handler": delete_tool_handler,
            "public": False
        }
    },
    "/tools": {
        "GET": {
            "handler": get_tools_handler,
            "public": False
        }
    },
    "/test-tool": {
        "POST": {
            "handler": test_tool_handler,
            "public": False
        }
    },
    "/sre": {
        "POST": {
            "handler": create_sre_handler,
            "public": False
        }
    },
    "/sre/{sre_id}": {
        "GET": {
            "handler": get_sre_handler,
            "public": False
        },
        "POST": {
            "handler": update_sre_handler,
            "public": False
        },
        "DELETE": {
            "handler": delete_sre_handler,
            "public": False
        }
    },
    "/sres": {
        "GET": {
            "handler": get_sres_handler,
            "public": False
        }
    },
    "/run-sre/{sre_id}": {
        "POST": {
            "handler": run_sre_handler,
            "public": True
        }
    },
   "/json-document": {
        "POST": {
            "handler": create_json_document_handler,
            "public": False
        }
    },
    "/json-document/{document_id}": {
        "GET": {
            "handler": get_json_document_handler,
            "public": True
        },
        "POST": {
            "handler": update_json_document_handler,
            "public": False
        },
        "DELETE": {
            "handler": delete_json_document_handler,
            "public": False
        }
    },
    "/json-documents": {
        "GET": {
            "handler": get_json_documents_handler,
            "public": False
        }
    },
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
                return_type = handler_info.get('return_type', 'application/json')  # Default to 'json' if 'return_type' key is missing
                return handler, params, is_public, return_type
    
    return None, None, None, None


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
        handler, request_params, is_public, return_type = match_route(request_path, request_method, handler_registry)
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
        return create_api_gateway_response(200, response.model_dump() if return_type == 'application/json' else response, return_type)
            

    # Return any errors   
    except Exception as e:
        logger.error(str(e))
        error, code = e.args if len(e.args) == 2 else (e, 500)
        return create_api_gateway_response(code, {
            'error': str(error)
        }, 'application/json')
