import json
from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Context, Agent, User
from Services import AgentService

def create_context_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> Context.FilteredContext:   
    
    # Get the body of the request
    body = Context.CreateContextParams(**json.loads(lambda_event.body))

    # Get the agent
    agent: Agent.Agent = None
    if user == None:
        agent = Agent.get_public_agent(body.agent_id)
    else:
        dbUser = User.get_user(user.sub)
        agent = Agent.get_agent_for_user(body.agent_id, dbUser)

    context = Context.create_context(body.agent_id, user.sub if user != None else None)

    if (body.invoke_agent_message or agent.agent_speaks_first):
        context = AgentService.invoke_context(context, agent)

    return Context.transform_to_filtered_context(context)


    


            