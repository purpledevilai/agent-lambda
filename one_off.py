from src.Models import Agent, User
from src.AWS import Cognito
from src.lambda_function import lambda_handler
from tests.helper_funcs import create_request
import json
import sys
sys.path.append("../")

access_token = "eyJraWQiOiJvV1VOKzZiYlQ5MmFRN2Q4RlwvVmFkQXByaFhuV3pQejJ4Y3M0R0JFQWJ3VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4Njc5NDViOC0zMDUxLTcwYmQtOWI4Ny02YWMzNzllYzA1YmUiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuYXAtc291dGhlYXN0LTQuYW1hem9uYXdzLmNvbVwvYXAtc291dGhlYXN0LTRfTmFmcVlvRzd2IiwiY2xpZW50X2lkIjoiMjA0aW82MDdtODcwczRnNjI2dm5tNnZpcXEiLCJvcmlnaW5fanRpIjoiMWZjY2QxYTQtMDAyYi00NjY0LWJkZDMtYTY3NTA5YmFmNzYwIiwiZXZlbnRfaWQiOiI0NTEzMWNjNS0xNjg1LTQwNjktYTI5NS05NzAzYjAxNzJhYmQiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNzM0OTAzNDUyLCJleHAiOjE3MzQ5NDE4ODQsImlhdCI6MTczNDkzODI4NCwianRpIjoiM2I2ZTU1NTAtMjhkZS00YzJhLWIxNDYtMGFjODE5MzVmYzVlIiwidXNlcm5hbWUiOiI4Njc5NDViOC0zMDUxLTcwYmQtOWI4Ny02YWMzNzllYzA1YmUifQ.MZsSkHWgtc9Vthm-ycWebbH1YRx-W2p4l6KEzF1nnIMKGE362HV1J4SJZrz8PKcNlmKRxBllYLYvaW-es4EvDAliJZh9bhIwvH7UhE0SEKZZpAKRV6vO2aazJ9HETA9GEVrWrftoTLL55TbsCF0uY9o42B7i9oVz3g-8KjJ_-VYKnYuDwSC3CGYP79WhqMqx80I--7gtMgwODbA-k3xaA9NN5ZHwNZtmq6zD8d1j-yfldVPSD74DKw53I_AWjW0ewRHbyjDXChcktq9Ldz-f9ITR7CBXZ8JF9C-alcpVNySJNBkFiUWB8lmLfEGHkKLWB7U1BZe-g1RpX_dZATlgxQ"

cognito_user = Cognito.get_user_from_cognito(access_token)
user = User.get_user(cognito_user.sub)

agent = Agent.create_agent(
    agent_name="Keanu",
    agent_description="A clone of Keanu",
    prompt="Just act like Keanu",
    org_id=user.organizations[0],
    is_public=False,
    agent_speaks_first=False,
)

print(json.dumps(agent.model_dump(), indent=4))

# Create request
# request = create_request(
#     method="POST",
#     path="/agent",
#     headers={
#         "Authorization": access_token
#     },
#     body={
#         "agent_name": "Test Agent",
#         "agent_description": "Test Description",
#         "prompt": "Test Prompt",
#         "is_public": False,
#         "agent_speaks_first": False
#     }
# )


# Make the call!!
# result = lambda_handler(event, None)
# print(json.dumps(json.loads(result["body"]), indent=4))
