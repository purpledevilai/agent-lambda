import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/context"
http_method = "GET"
query_string_parameters = {
    #"context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a"
}
body = {
    "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a",
    "message": "What's the deal with airline food?",
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTciLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiZmE2M2M1YmMtMmExMy00NGE0LTg5MTgtOTc4ZTlkYzVjZjNmIiwiZXZlbnRfaWQiOiJiNjZlNjY2Yi0wNGE4LTRkMDEtYmRiZS03ZjQ0MmY1ZGRkYjYiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMxNTU4ODg5LCJleHAiOjE3MzE2NjMwNTgsImlhdCI6MTczMTY1OTQ1OCwianRpIjoiYmVhMjY3ZjgtODhiZS00NGIxLWI2ZjYtZGNiMDdlYzlmOWRlIiwidXNlcm5hbWUiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTcifQ.aBhzGi3H4_InVu51CnWMvCcd3J2W5aLHNQ-BfRTLqOOwgPJAXaljRJNgg6md0n9ZwMqEdOKdWgoohvDsyUECFF_UOf_gK5tInS7ypzd9WpIsuOgKkFaU8JQRXrjRj1SlR15ovVkbr9nMq80tDme9L6C2Qbt25qtbLKh1_a7_1AGi1I8bTeBSHHluJJMiWbpI3JpAeq6JUONhS4dbEw5fzSIgvm2j1cM36pxbbMG13dBIXnd46yU89e0u6pUxXLShh6yLO-Z-hSFwREVL22Gu9-ghHepWdOvZBmvTPfHxKNNnB1G1SNOY_tkVDolTBvMEfoNnCZdsMHBVrdLtT5RiHw"

event = {
  "path": path,
  "httpMethod": http_method,
  "queryStringParameters": None,
  "headers": {
    "Authorization": access_token
  },
  "body": json.dumps(body) if http_method == "POST" else None,
}



# Make the call!!
result = lambda_handler(event, None)
print(json.dumps(json.loads(result["body"]), indent=4))
