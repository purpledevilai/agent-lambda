import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/chat-history"
http_method = "GET"
query_string_parameters = {
    #"context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a"
}
body = {
    "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a",
    "message": "What's the deal with airline food?",
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTciLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiZmE2M2M1YmMtMmExMy00NGE0LTg5MTgtOTc4ZTlkYzVjZjNmIiwiZXZlbnRfaWQiOiJiNjZlNjY2Yi0wNGE4LTRkMDEtYmRiZS03ZjQ0MmY1ZGRkYjYiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMxNTU4ODg5LCJleHAiOjE3MzE2NTkzOTUsImlhdCI6MTczMTY1NTc5NSwianRpIjoiZjAzNGUxOTUtYmEyNy00N2Y4LTkyODMtZDQxMzEwMmMwMGUzIiwidXNlcm5hbWUiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTcifQ.Vli_-U7js8OOaYgvtafmEg8sKFFrMIgZW201b51iSZiZ01n0tg2H3oznw5M80-J16eJBOXtcOhMrdGCMW_NLoP9vAQWfSfVMQIBaRoHcJXfk69Sn_pibSH6J99T5rkZAofIvUHHtay0I25zXcjG9OMdQC0UdcyoGaSjhTI36EcwhNrHse1JrIjek4qfUHrcQbzAyQiOS1NLcUiOspiXjdY5oVj9iv_bt_x4TzkoKjzluOS2ryhhIFySFY4qh4SuSMD6NSglPEeLbeu3HC7AJYmCvXDS0H0fTY7Lczn5ocmMq7T4KnZz8ksPvCdkba_CcBtstlwLJsmQg0OdW7ADTyw"

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
