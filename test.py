import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/chat-history"
http_method = "GET"
body = {
    #"context_id": "91f668d6-4536-42ec-8bd0-9c446286404f",
    "message": "Hey, my name is Cowboy. How are you?",
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIyNmU5MTU5OC1hMGIxLTcwMzYtNGM5OS04MTZmOGZiMjBiOGYiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiNjIxZTQ1YTEtYWVhMi00ZjY0LWFiZDctODdhZGYzYjYzZDU1IiwiZXZlbnRfaWQiOiJiNmEyYmZjNy05ZWU1LTQ2YWItOGExMy1kMTkwYWMwMDNmMDMiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMxMzIyMzQ5LCJleHAiOjE3MzEzNTk2MjcsImlhdCI6MTczMTM1NjAyNywianRpIjoiYzNkMDRiN2EtMWM3MC00OTI4LThlOTgtM2NlODIyN2FlYmNhIiwidXNlcm5hbWUiOiIyNmU5MTU5OC1hMGIxLTcwMzYtNGM5OS04MTZmOGZiMjBiOGYifQ.L3g_wTTbExm629CLJ9z85lIzQISkqcbOuY_1WoXWALrFoBhNRkrA5XyCXUoVWrLBcucWQfPZdan1S8GA5Ii8GVc7riEn1iB5y8aQbezvdsXr-yAFS0VaM9-wWB6esg8JclT8aFyw6StjZZ847EUIJj9ovWiERjccSzb2Sw4ToAcdPkjTm8Ur275ut2vPC8dYoPtgqP-ReadDs65cltmVRQHqLkNFKGYD8jhe8etlcSroq7zlrWb04mc3xaEgTHTMIxFMQcNjJrxZKrcXNNShTBIrISn3UDMTkSw4mRPLljNP_8JTvPHs200U8bKb3mIawAKqEpJQc3zjvNWNu829OA"

event = {
  "resource": path,
  "path": path,
  "httpMethod": http_method,
  "headers": {
    "Authorization": access_token
  },
  "body": json.dumps(body) if http_method == "POST" else None,
}



# Make the call!!
result = lambda_handler(event, None)
print(json.dumps(json.loads(result["body"]), indent=4))
