import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

body = {
    #"context_id": "91f668d6-4536-42ec-8bd0-9c446286404f",
    "message": "Hey, my name is Cowboy. How are you?",
}

event = {
  "resource": "/chat",
  "path": "/chat",
  "httpMethod": "POST",
  "headers": {
    "Authorization": "access-token"
  },
  "body": json.dumps(body)
}

get_chat_history_event = {
  "resource": "/chat_history",
  "path": "/chat_history",
  "httpMethod": "GET",
  "headers": {
    "Authorization": "access-token"
  }
}



# Make the call!!
result = lambda_handler(get_chat_history_event, None)
print(json.dumps(json.loads(result["body"]), indent=4))
