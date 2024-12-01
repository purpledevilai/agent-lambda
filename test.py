import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/chat"
http_method = "POST"
query_string_parameters = {
    #"context_id": "f0247aa4-99e6-4749-b074-7d99fda5c3db",
    "agent_id": "aj-prompt-engineer",
    "invoke_agent_message": "true",
}
body = {
    "context_id": "cc997a09-bd20-4af6-b1f5-c85f53fb446b",
    "message": "Yeah can you make a prompt that simply says 'Hello, how can I help you today?'",
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxNjQ5MjUzOC00MDgxLTcwYWEtYjJhMS00ZmJkZThhMWFmNmEiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiYzRkMjY0NmUtNTk0Zi00MTMxLThiNmUtMDg5ZjgwY2U0MzM5IiwiZXZlbnRfaWQiOiJhYjk5YmZjOS1hMzM0LTQ2OTktYTY1ZS02NWE2MDBjMDU5YTEiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMzMDE0OTU0LCJleHAiOjE3MzMwOTQwMjAsImlhdCI6MTczMzA5MDQyMCwianRpIjoiNTY4OGY3YmQtNWZhOC00MTUyLWE3MzQtMmM4NWZiZDM0OWYwIiwidXNlcm5hbWUiOiIxNjQ5MjUzOC00MDgxLTcwYWEtYjJhMS00ZmJkZThhMWFmNmEifQ.tQ4UM0AxA7RxzxVBrJXpGwy2uXzZ-7R9svpcEcJK1r09_baXQv8DzHmpXKSer-EF8T5T1kv_Fv91Qjf1y3AZ6f9VAJGS4LBeWYXapd444l3sSNhKMbDLjZb8s45SJaVaugJwAeSWRm9xFkFKMwrRlFZCCo6zSFvTJWoc5dHZUgVxlbn-urAe6xtCLLHpz-xlZTvdzaqmM1v5ZrtuE1J0b4gHpYboh6I63KFthBxkTLwkqQG8wbZMit2BsaahtngWqIzTf6_pxoYQn88thtQz85WMs8p21IA0hfqI2ssL2qEaODuaz36pdg6TYxAigQMvtscaASUACxIR-mg-uK-rvQ"

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
