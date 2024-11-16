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
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIyNmU5MTU5OC1hMGIxLTcwMzYtNGM5OS04MTZmOGZiMjBiOGYiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiNTk2OGIzNmYtNTUwZS00OWQ2LWI5YjQtMGY3NTRkZmI3ZDZlIiwiZXZlbnRfaWQiOiI1ZmY5NTJmYS1jYTc4LTRjMjAtYjMzZi1lNDUxMjU0NzVkY2EiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMxNzIzNDIxLCJleHAiOjE3MzE3MzUwNjAsImlhdCI6MTczMTczMTQ2MCwianRpIjoiOTgyZmViNWMtNGNiMS00OGQxLTgzN2MtNTJkZjYzMjVhMmYyIiwidXNlcm5hbWUiOiIyNmU5MTU5OC1hMGIxLTcwMzYtNGM5OS04MTZmOGZiMjBiOGYifQ.B2zQi_qY-SVE7hPnAEAcBYCCFEiH8VE_h8icxIHgFRqweXVd5IPj5fwoic8akw5ig_qLBJNDgRHDfnuwvqbO0MzwqWjr6pTItD7aLng21S76bigncYrKVOEkoWP77D-6XPokUVezvcp1MSe6wbQ2ZtZAhoW1xLQRPmilr-pxPA6u_sNnSqPY9eA-8ePOAfK6tlpWGUWZCvWGnXb3E5JVpyCYgNGM3orZaY3tmEBN9ef4ryi0n1z4rVRfSIyP7vVwm3AVqQpHlrW7c94mpigEZ2LmVkyZwcaSDz9tstPQtPJoM6uNiQWdoN_DHJK64OtFWddLnOiuBLI7L1cHm3eU_w"

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
