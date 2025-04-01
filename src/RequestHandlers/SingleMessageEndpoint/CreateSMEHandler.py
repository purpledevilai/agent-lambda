import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import SingleMessageEndpoint as SME
from Models import User, ParameterDefinition


def create_sme_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SME.SingleMessageEndpoint:
    dbUser = User.get_user(user.sub)

    # Parse and validate request body
    body = SME.CreateSMEParams(**json.loads(lambda_event.body))
    
    # Default to first organization if org_id is not provided
    if body.org_id is None:
        body.org_id = dbUser.organizations[0]
    elif body.org_id not in dbUser.organizations:
        raise Exception("User does not have access to this organization", 403)

    # Validate that the user has access to the parameter definition
    ParameterDefinition.get_parameter_definition_for_user(body.pd_id, dbUser)

    # Create the SME
    sme = SME.create_sme(
        org_id=body.org_id,
        name=body.name,
        description=body.description,
        pd_id=body.pd_id,
        is_public=body.is_public,
    )

    return sme