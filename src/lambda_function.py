import uuid
from RequestHandlers.AgentMessageHandler import agent_message_handler


# LAMBDA HANDLER - What gets called when a request is made. event has any data that's passed in the request
def lambda_handler(event, context):
    try:
        # Check for required params
        if "message" not in event:
            raise Exception("No message provided")
        
        # Create context_id if none provided
        if "context_id" not in event or event["context_id"] == "":
            event["context_id"] = str(uuid.uuid4())

        # Check for agent name and set to default if not provided
        if "agent_name" not in event or event["agent_name"] == "":
            event["agent_name"] = "default"
            
        # Get the message and conversation ID
        message = event["message"]
        context_id = event["context_id"]
        agent_name = event["agent_name"]

        return agent_message_handler(agent_name, message, context_id)

    # Return any errors   
    except Exception as e:
        return {
            'error': str(e)
        }
