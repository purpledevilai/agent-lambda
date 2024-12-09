import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/user"
http_method = "GET"
query_string_parameters = {
    #"context_id": "f0247aa4-99e6-4749-b074-7d99fda5c3db",
    # "agent_id": "aj-prompt-engineer",
    # "invoke_agent_message": "true",
}
body = {
    # "context_id": "cc997a09-bd20-4af6-b1f5-c85f53fb446b",
    # "message": "Yeah can you make a prompt that simply says 'Hello, how can I help you today?'",
    "agent_id": "ac4d1802-4ff0-4f4b-8b9d-ac38a3f6e2f1",
    "prompt": "You are a professional prompt engineer, that is also really funny",

}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJiNjg5YjUwOC01MGYxLTcwMDgtNTc5ZS03OTEwZDQ2NDBmYWUiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiMzQ2NDNlOTQtNTRiNy00MWZlLWEwODYtZTc2MmUwMDNiM2JkIiwiZXZlbnRfaWQiOiIyM2E3YTBkYS1hODUyLTRmYTctOWIyMS0xOTk0ZTBiMGNmZjciLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMzNzc5Mzk2LCJleHAiOjE3MzM3ODI5OTYsImlhdCI6MTczMzc3OTM5NiwianRpIjoiYzIwM2Y1MjgtYjQ0ZC00NjQ5LWIwN2UtMzhlMjc0MzAwOTcwIiwidXNlcm5hbWUiOiJiNjg5YjUwOC01MGYxLTcwMDgtNTc5ZS03OTEwZDQ2NDBmYWUifQ.T5qTHEkQ0xaFnhvWVxt2P950Vo3KppkxZO7ylCx0169aPA3pYg94CeyAV5Jv461mFDewopcWGbn9ncVKgaXUndnQ507DzVi1ybbRFlPMlVFQaq5vyvyBmohngEZ8wwWZefznJRFJcL-4bUd49nb4yXAdjbBUKR2tZFV3XaYkSqyuucQF87CW1jiy7X5U7lL337gIwFnB2mCXYfIbAXR2AohF7I7Uhg9INZjvYHZve3rxB2nIZIt-31J3kYgz8YfzIKJ8OmKQgBPznAReNhWKfacASYxcVyIN0DlMdPN0q2gkOzzpRwx2LDpnA3dloMXt0dD3utdSpe04lvf0IadMeQ"

event = {
  "path": path,
  "httpMethod": http_method,
  "queryStringParameters": query_string_parameters,
  "headers": {
    "Authorization": access_token
  },
  "body": json.dumps(body) if http_method == "POST" else None,
}



# Make the call!!
result = lambda_handler(event, None)
print(json.dumps(json.loads(result["body"]), indent=4))
