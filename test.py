import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

event = {
    "context_id": "fe980400-be4d-4781-bf56-326c602a6df3",
    "message": "Lets do monday, at 10am",
}

# Make the call!!
result = lambda_handler(event, None)
print(json.dumps(result, indent=4))
