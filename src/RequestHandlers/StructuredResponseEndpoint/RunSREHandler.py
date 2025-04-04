import json
from typing import Optional
from LLM.LLMExtract import llm_extract
from LLM.CreateLLM import create_llm
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import StructuredResponseEndpoint as SRE, User, ParameterDefinition
from pydantic import BaseModel

class RunSREParams(BaseModel):
    prompt: str


def run_sre_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]):

    # Get the sre id from url
    sre_id = lambda_event.requestParameters.get("sre_id")
    if not sre_id:
        raise Exception("sre_id is required", 400)

    # Extract the prompt from the request body
    body = RunSREParams(**json.loads(lambda_event.body))
    prompt = body.prompt

    # Get the SRE
    sre = None
    if (user):
        dbUser = User.get_user(user.sub)
        sre = SRE.get_sre_for_user(sre_id, dbUser)
    else:
        sre = SRE.get_public_sre(sre_id)

    # Get parameter definition from sre
    pd = ParameterDefinition.get_parameter_definition(sre.pd_id)

    # Create the pydantic class that will be the output of the LLM
    extract_object = ParameterDefinition.create_pydantic_class(sre.name, pd.parameters, docstring=sre.description)

    # Run the LLM
    llm_response = llm_extract(extract_object, prompt, create_llm())

    return extract_object(**llm_response)

    

    

