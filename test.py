import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/context"
http_method = "GET"
query_string_parameters = {
    #"context_id": "f0247aa4-99e6-4749-b074-7d99fda5c3db",
    "agent_id": "aj-prompt-engineer",
    "invoke_agent_message": "true",
}
body = {
    "context_id": "f0247aa4-99e6-4749-b074-7d99fda5c3db",
    "message": "What's the deal with airline food?",
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxNjQ5MjUzOC00MDgxLTcwYWEtYjJhMS00ZmJkZThhMWFmNmEiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiYzRkMjY0NmUtNTk0Zi00MTMxLThiNmUtMDg5ZjgwY2U0MzM5IiwiZXZlbnRfaWQiOiJhYjk5YmZjOS1hMzM0LTQ2OTktYTY1ZS02NWE2MDBjMDU5YTEiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMzMDE0OTU0LCJleHAiOjE3MzMwMzgxODIsImlhdCI6MTczMzAzNDU4MiwianRpIjoiODk1YTExODUtZTRiNS00MzZiLWI0ZWQtYTMwYWJlZjA4NzNiIiwidXNlcm5hbWUiOiIxNjQ5MjUzOC00MDgxLTcwYWEtYjJhMS00ZmJkZThhMWFmNmEifQ.rbP-lSeypZBwAY0CQCHWtZU8amNYirXEBuboqafM-bDlfN36SgdLHccZ1vSwvKqYm1KiOIjd9bS27fP8WpsZFdB5K9lxp3PwYbei32Do0arXuK4GUQobbAa9UcNxSUs3QhNJ0OminUsFnCtkEpFmEY0FgmcrX5SbUCsdAAxdc3dnXZyV4O110-tZssnoIjmAfRqVjvdNvq_kKiR8g3XWAZRHxZElBfTMVoFXdvcSUU_gJ0cR3SmnsD_Vk0_YIJRFlbJBiuXV6PZp87aGgdtAFu8wj_ZDr70DZQKrTf-k5vvzOhVaQzI_SPHogMqUclTkg0NpgSqdP4JZt3-Ylong1w"

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
