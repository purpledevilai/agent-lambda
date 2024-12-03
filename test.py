import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/agent"
http_method = "POST"
query_string_parameters = {
    #"context_id": "f0247aa4-99e6-4749-b074-7d99fda5c3db",
    "agent_id": "aj-prompt-engineer",
    "invoke_agent_message": "true",
}
body = {
    # "context_id": "cc997a09-bd20-4af6-b1f5-c85f53fb446b",
    # "message": "Yeah can you make a prompt that simply says 'Hello, how can I help you today?'",
    "agent_id": "ac4d1802-4ff0-4f4b-8b9d-ac38a3f6e2f1",
    "prompt": "You are a professional prompt engineer, that is also really funny",

}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxNjQ5MjUzOC00MDgxLTcwYWEtYjJhMS00ZmJkZThhMWFmNmEiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiYzRkMjY0NmUtNTk0Zi00MTMxLThiNmUtMDg5ZjgwY2U0MzM5IiwiZXZlbnRfaWQiOiJhYjk5YmZjOS1hMzM0LTQ2OTktYTY1ZS02NWE2MDBjMDU5YTEiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMzMDE0OTU0LCJleHAiOjE3MzMyMTQxNzksImlhdCI6MTczMzIxMDU3OSwianRpIjoiNjU1ZDBkMjUtMWE1Yy00ZTM4LWIwNGUtYjkzZWU0MWFmMDc1IiwidXNlcm5hbWUiOiIxNjQ5MjUzOC00MDgxLTcwYWEtYjJhMS00ZmJkZThhMWFmNmEifQ.GVtkbX0TdpQg54TxDEH-L0tqoC75NMVbPnFUiD3nMIoR3fgDfgkyWkqB5ZEjkr4Qhhv4g92I5kRvqxi6YVCkJr8fzeGNR304um3eb8w_yl2HEQd1HtYMNuGrYPoyLUvwMj10jVofrT7Cuswwf8YEnrRMbfcVBYa_VInpl6uUocNKZYHFBHvVfXdNBBuHKddZHAs08kZLAcrsAmN9lycgNRU7yO76j7iWlawcM01hbS61HePem7oqPuErmy952QZFBQNhtfDwNSQnY6QEi9RujXOwZhpbPK4Q7W6ds_v4LaDVU-QbpW31PbbUuCBvE-ezWI4kIdCILUDPlhQKeK2zzg"

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
