import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

body = {
    #"context_id": "91f668d6-4536-42ec-8bd0-9c446286404f",
    "message": "Hey, my name is Keanu. How are you?",
}

event = {
  "headers": {
    "Authorization": "access_token",
  },
  "body": json.dumps(body),
}

# Make the call!!
result = lambda_handler(event, None)
print(json.dumps(result, indent=4))
