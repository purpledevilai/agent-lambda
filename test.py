import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/chat-history"
http_method = "GET"
query_string_parameters = {
    "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a"
}
body = {
    "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a",
    "message": "What's the deal with airline food?",
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTciLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiYTQwOGU0NmYtZTZlZi00ZDFmLWFmNmMtNTc0YWZkYTllODc0IiwiZXZlbnRfaWQiOiJiYWVkYTJhYi02ZjhjLTQwNWUtODY5Yy00ZWEwZTEyNmJlOTYiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMxNzQzMDk2LCJleHAiOjE3MzE4Mjk1MDksImlhdCI6MTczMTgyNTkwOSwianRpIjoiYWQ3M2YxZTEtMjQ1ZC00YWYyLWJhZjctYTRlMmY4NTc3MzE4IiwidXNlcm5hbWUiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTcifQ.r3Vl3q8c7j5ZZyJAxT-YiljbCvTAXnES1H5x6On6dTs6Zt9tFIKctDeJ7ICOOJEqhBQI-luE9OFDlz77DLN51kQUBuM_L8ixLjB7_8tI4z18jP2AytY5doO8Mh64pmZmPjBQ7mWOI7iiWmfu3ObN8eTAFt6DzteVcmzB6sVVyK9NFt-s16aOFUg2T-9APJrV4b-sNTUw4e6gxrSRmF43Kj5i0V3lk0CjQcfcNB8WqFku9KrSEXQjAO2BeuKocG0_ur54dce2mEoyd-AvGiei1oyxN8G7RQqaocNKBzVepI4NLu8ZV1qVnA0nUC3LKdhO_hn8Cqp537633AhjjDpkgA"

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
