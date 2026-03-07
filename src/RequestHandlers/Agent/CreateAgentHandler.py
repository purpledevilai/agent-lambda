import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Agent, User, Tool
from Models.LLMModel import validate_model_id, is_anthropic_model

def create_agent_handler(lambda_event: LambdaEvent, user: CognitoUser) -> Agent.Agent:   
    
    dbUser = User.get_user(user.sub)

    # Get the body of the request
    body = Agent.CreateAgentParams(**json.loads(lambda_event.body))
    if (body.org_id == None):
        body.org_id = dbUser.organizations[0]
    elif (body.org_id not in dbUser.organizations):
        raise Exception("User does not have access to this organization", 403)

    if (body.tools):
        Tool.validate_tools_for_user(body.tools, dbUser)

    if body.model_id:
        validate_model_id(body.model_id)
        if body.agent_speaks_first and is_anthropic_model(body.model_id):
            raise Exception("Anthropic models do not support agent_speaks_first", 400)

    # Create the agent
    agent = Agent.create_agent(
        agent_name=body.agent_name,
        agent_description=body.agent_description,
        prompt=body.prompt,
        org_id=body.org_id,
        is_public=body.is_public,
        agent_speaks_first=body.agent_speaks_first,
        tools=body.tools,
        voice_id=body.voice_id,
        uses_prompt_args=True if body.uses_prompt_args else False,
        prompt_arg_names=body.prompt_arg_names if body.prompt_arg_names else [],
        initialize_tool_id=body.initialize_tool_id,
        model_id=body.model_id,
    )

    return agent


    


            