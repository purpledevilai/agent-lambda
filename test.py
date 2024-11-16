import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/agents"
http_method = "GET"
query_string_parameters = {
    "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a"
}
body = {
    "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a",
    "message": "What's the deal with airline food?",
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIyNmU5MTU5OC1hMGIxLTcwMzYtNGM5OS04MTZmOGZiMjBiOGYiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiNTk2OGIzNmYtNTUwZS00OWQ2LWI5YjQtMGY3NTRkZmI3ZDZlIiwiZXZlbnRfaWQiOiI1ZmY5NTJmYS1jYTc4LTRjMjAtYjMzZi1lNDUxMjU0NzVkY2EiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMxNzIzNDIxLCJleHAiOjE3MzE3MzA3MTMsImlhdCI6MTczMTcyNzExMywianRpIjoiZTU2ZTYzYWMtYzQxZC00YWUxLTlhYzAtYzkyM2Q5MjdiY2Q0IiwidXNlcm5hbWUiOiIyNmU5MTU5OC1hMGIxLTcwMzYtNGM5OS04MTZmOGZiMjBiOGYifQ.YC3rgH_cbDCC1T36P99KzNLGoy2M0fjJrA6-a-v0Em1GSov1x7Q2OxPe9Wea0W0kPpVJaoxY4yyO9UVdmlliWGVCFgShw66wY-U2Ptfyk0rq4BpJV2WutZi3TqdHhNVs038N8vLWA5pr6wK_AN7CSpuT93QO_UhA77olv2Y8s4nNeyPFoJmvpMi_cvgDAJJ6GT2xId_4hHTctiCNE3vczztrr5kLz65IJvzX5CLhRjpTLhg6W-FFmpJVnzcuntOi_psUOgypCLzY0JjLd2XT6Vd2fzAO8Ej5ykhw5YrY0zvXFfPqYe6z-t52f221_DH-9tgCasCmtQA0FccoDZPTlQ"

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
