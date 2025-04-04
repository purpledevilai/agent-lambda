import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import StructuredResponseEndpoint as SRE, User, ParameterDefinition

def update_sre_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SRE.StructuredResponseEndpoint:
    # Parse update body
    body = SRE.UpdateSREParams(**json.loads(lambda_event.body))

    # Retrieve SRE ID
    sre_id = lambda_event.requestParameters.get("sre_id")
    if not sre_id:
        raise Exception("sre_id is required", 400)

    # Get user and SRE
    dbUser = User.get_user(user.sub)
    sre = SRE.get_sre_for_user(sre_id, dbUser)

    # Validate parameter definition access, if updated
    if body.pd_id:
        ParameterDefinition.get_parameter_definition_for_user(body.pd_id, dbUser)

    # Merge updated fields
    update_dict = {k: v for k, v in body.model_dump().items() if v is not None}
    sre_dict = sre.model_dump()
    sre_dict.update(update_dict)
    updated_sre = SRE.StructuredResponseEndpoint(**sre_dict)

    # Save and return
    SRE.save_sre(updated_sre)
    return updated_sre
