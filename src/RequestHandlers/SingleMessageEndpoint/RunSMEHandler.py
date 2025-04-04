import json
from typing import Optional
from LLM.LLMExtract import llm_extract
from LLM.CreateLLM import create_llm
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import SingleMessageEndpoint as SME, User, ParameterDefinition
from pydantic import BaseModel

class RunSMEParams(BaseModel):
    message: str


def run_sme_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]):

    # Get the sme id from url
    sme_id = lambda_event.requestParameters.get("sme_id")
    if not sme_id:
        raise Exception("sme_id is required", 400)

    # Extract the message from the request body
    body = RunSMEParams(**json.loads(lambda_event.body))
    message = body.message

    # Get the SME
    sme = None
    if (user):
        dbUser = User.get_user(user.sub)
        sme = SME.get_sme_for_user(sme_id, dbUser)
    else:
        sme = SME.get_public_sme(sme_id)

    # Get parameter definition from sme
    pd = ParameterDefinition.get_parameter_definition(sme.pd_id)

    # Create the pydantic class that will be the output of the LLM
    extract_object = ParameterDefinition.create_pydantic_class(sme.name, pd.parameters, docstring=sme.description)

    # Run the LLM
    llm_response = llm_extract(extract_object, message, create_llm())

    return extract_object(**llm_response)

    

    

