import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/context"
http_method = "GET"
query_string_parameters = {
    "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a"
}
body = {
    "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a",
    "message": "What's the deal with airline food?",
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTciLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiZmE2M2M1YmMtMmExMy00NGE0LTg5MTgtOTc4ZTlkYzVjZjNmIiwiZXZlbnRfaWQiOiJiNjZlNjY2Yi0wNGE4LTRkMDEtYmRiZS03ZjQ0MmY1ZGRkYjYiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMxNTU4ODg5LCJleHAiOjE3MzE3MTk2MDEsImlhdCI6MTczMTcxNjAwMSwianRpIjoiZWM5NGE2MGYtYzBlZi00MmE3LTgwYzgtZjI5ZDQxYmJlZDgzIiwidXNlcm5hbWUiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTcifQ.Ftiom89aRTZGaUAEFeVXIbDkA-ZqUi0k-r1Nh-vFE3GYKS00VnZFTSDhOSr2H6wurrOpjOyciwa2R7GQ5h2Qr5uLy1l8wF3yV7bZ6Z0CKnxMyDrRnz1RkqZtqNWrNUaa20KpbCvp3eYjmb41omR9skHPTLMrlQJR7fD722ObT327jBV1VcCGh-hT6Jmzx-EN9VoDqic4zyb3yOK8YpT_tTu6maxgSFOhXLdGdA2OAbvrVt0eUM2_uGNezLwQ9zOrNpQ9TqTPZpEksQarQYe6uV_fIap-2_tLFnk9U2n3nABH48YIBxpZzt27fwaBmTpZkPxCJcukmS9kb4kmBZDrCg"

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
