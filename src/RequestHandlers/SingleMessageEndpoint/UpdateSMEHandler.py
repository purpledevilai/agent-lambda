import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import SingleMessageEndpoint as SME, User, ParameterDefinition

def update_sme_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SME.SingleMessageEndpoint:
    # Parse update body
    body = SME.UpdateSMEParams(**json.loads(lambda_event.body))

    # Retrieve SME ID
    sme_id = lambda_event.requestParameters.get("sme_id")
    if not sme_id:
        raise Exception("sme_id is required", 400)

    # Get user and SME
    dbUser = User.get_user(user.sub)
    sme = SME.get_sme_for_user(sme_id, dbUser)

    # Validate parameter definition access, if updated
    if body.pd_id:
        ParameterDefinition.get_parameter_definition_for_user(body.pd_id, dbUser)

    # Merge updated fields
    update_dict = {k: v for k, v in body.model_dump().items() if v is not None}
    sme_dict = sme.model_dump()
    sme_dict.update(update_dict)
    updated_sme = SME.SingleMessageEndpoint(**sme_dict)

    # Save and return
    SME.save_sme(updated_sme)
    return updated_sme
