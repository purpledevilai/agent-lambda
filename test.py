import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/agents"
http_method = "GET"
query_string_parameters = {
    #"context_id": "f0247aa4-99e6-4749-b074-7d99fda5c3db",
    #"agent_id": "rebin-agent"
}
body = {
    "context_id": "f0247aa4-99e6-4749-b074-7d99fda5c3db",
    "message": "What's the deal with airline food?",
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxNjQ5MjUzOC00MDgxLTcwYWEtYjJhMS00ZmJkZThhMWFmNmEiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiYWM5N2M1NDktMTE2ZS00ZTk2LTlmNWYtYWQxZWI0YWViNzE0IiwiZXZlbnRfaWQiOiIzNDNlOGM5Ny0zNjM5LTQxNjUtYWZjNi0wMjRhODFlNDE2ZmQiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMyOTQxODM5LCJleHAiOjE3MzI5NDU0MzksImlhdCI6MTczMjk0MTgzOSwianRpIjoiYmIwOGFjYTYtOGE2NC00NDNlLWE2N2UtZDAwODRjMjljYWY0IiwidXNlcm5hbWUiOiIxNjQ5MjUzOC00MDgxLTcwYWEtYjJhMS00ZmJkZThhMWFmNmEifQ.XzGvTK17Zbu4dHAO63hbvGxNYAgXpBWBkTjpPtn_o3cFp_PJvlI4dvQOpAUOHzSeCNnhh29_fTh7JenKth465U0Y6s16tXR1IKpt5CMiAMHM0FCTglM0GqPtzmTmcVLLCsYjHrNeKVqm0ZYKsPbVuazRAGThaCTp7GKmAfIzzXTxO-BHZgNS4-bqPxkJ9B9VcQQJUl69vLjp1mmxUZUam5RtbNXHBR_VTZlaUXUvOBujFLD4et_VtvSdewqPW6gRIAAvoIgj91DYF3x9wBNo3WrjR-gfjvVslyaqud2iWZkSE8En9YeZfke9uSkVHuHaII3qvD4bwaA1mCUedyIVhw"

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
