import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/organization"
http_method = "POST"
query_string_parameters = {
    "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a"
}
body = {
    # "context_id": "fa2ea6ce-746e-4316-81ed-53eaf110564a",
    # "message": "What's the deal with airline food?",
    "name": "Keanu's Org"
}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTciLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiZDA4MDA2OGYtYzM5OC00YzM3LWEyZGMtOTA5NjRhMmRhM2MyIiwiZXZlbnRfaWQiOiI3OGYwNGZkZC0yZGIyLTQ1NGQtOGYyZS0zZTdmNDAyMGU4ZTMiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMxODc4MjQyLCJleHAiOjE3MzE5MTQ2ODMsImlhdCI6MTczMTkxMTA4MywianRpIjoiMTVmNDEyYTUtMTMxMy00Mjc1LWFkMmQtY2NmY2E1MjhjMWZlIiwidXNlcm5hbWUiOiI4Njc5YjUxOC0yMDgxLTcwYTktZDU0Zi04NWJjZDVmOTNjNTcifQ.e_tFL9m31Xu0ti6CnGjigo5pROMJ0qK0ar3G1dV1giB4jCVcMygZZL9ZxqIlTzE2LHVuHrRaIO0KfYaB-4abDfzgYnDzUqlRxq7guItDYtVXNk1O4k45ONuxWI4tUNGhs5ol1WChStgIWnMBYWy7EmaD-QdjLkmITltsmqbYBbHCMo2VDatFzp0AjRgz4nhGBGQyJUFWCzvkqUiPwUiMErC4e6VK_XHOy4agtTNMy6SE17rbWKge7wwmEPYS5hijdLyGfLnr66natGr2GORBepWZ5r0Lc-fkHpRNalP_dFWK-OUu2P8LMRTjXj_9BNZcn9uOakvFkMHTeSPeAjY1_Q"

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
