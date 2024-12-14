import sys
sys.path.append("./")
import json
from src.lambda_function import lambda_handler

path = "/context-history"
http_method = "GET"
query_string_parameters = {
    #"context_id": "f0247aa4-99e6-4749-b074-7d99fda5c3db",
    # "agent_id": "aj-prompt-engineer",
    # "invoke_agent_message": "true",
}
body = {
    # "context_id": "cc997a09-bd20-4af6-b1f5-c85f53fb446b",
    # "message": "Yeah can you make a prompt that simply says 'Hello, how can I help you today?'",
    "agent_id": "ac4d1802-4ff0-4f4b-8b9d-ac38a3f6e2f1",
    "prompt": "You are a professional prompt engineer, that is also really funny",

}
access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJiNjg5YjUwOC01MGYxLTcwMDgtNTc5ZS03OTEwZDQ2NDBmYWUiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiNWI1ODY4NDUtN2MxYy00OGIzLWJkZjktMWI3YmE5YjMxY2VhIiwiZXZlbnRfaWQiOiJlY2FiNWUyMy1kNTc4LTQ1M2MtOTlkMi1mMzc2NTQyMmI4YmYiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzMzODgwODc3LCJleHAiOjE3MzQxNTcyMDgsImlhdCI6MTczNDE1MzYwOCwianRpIjoiOTRiODNiZGEtNTNkOC00MDJiLWFlODYtNzUwOWQzYzliNDdhIiwidXNlcm5hbWUiOiJiNjg5YjUwOC01MGYxLTcwMDgtNTc5ZS03OTEwZDQ2NDBmYWUifQ.HMYX00p6I4QcJXt49ETzMmiMIASPCUYky9HaUtEMYCbfjvQjia7sz2pyQEeIu1j5Y5fYzItVUH_Y6dQ5a2A1RW9N9VYRRhZ9QRwP5czx1OpmofSaop9j2n82EhwZWAvckp7h_eYZkKA2IVc5am1YPpeTq8ZE0XLjbI28Vs8ywRaT4X5xVv3S4nyNK2AuDRCbVi8wqeiwHY0DOC3Ff41-y1QEqlVyEFrJlIyk7ykNrJU5AeLSg5xEs4VHmki3R8RLHYPl-GOePThHa8byEqfwcAlrgsojGr8hDtTacHmAjnXB_CV6pLOfeYreNNGm17uEIDju5wEXYEU69dcWViibmQ"

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
