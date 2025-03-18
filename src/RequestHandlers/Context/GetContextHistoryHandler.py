from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import Context, Agent
from pydantic import BaseModel

class ContextHistoryResponse(BaseModel):
    contexts: list[Context.HistoryContext]

def get_context_history_handler(lambda_event: LambdaEvent, user: CognitoUser) -> ContextHistoryResponse: 
    contexts = Context.get_contexts_by_user_id(user.sub)

    agent_ids = set()
    for context in contexts:
        agent_ids.add(context.agent_id)

    agents = {agent.agent_id: agent for agent in Agent.get_agents_from_ids(list(agent_ids))}

    return_contexts: list[Context.HistoryContext] = []
    for context in contexts:
        if context.agent_id not in agents:
            continue
        agent = agents[context.agent_id]
        history_context = Context.transform_to_history_context(context, agent)
        return_contexts.append(history_context)

    # Sort the contexts by time_stamp
    return_contexts.sort(key=lambda x: x.updated_at, reverse=True)

    return ContextHistoryResponse(**{
        "contexts": return_contexts
    })


    


            