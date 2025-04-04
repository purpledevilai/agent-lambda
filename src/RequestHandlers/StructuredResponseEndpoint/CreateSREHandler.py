import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import StructuredResponseEndpoint as SRE
from Models import User, ParameterDefinition


def create_sre_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SRE.StructuredResponseEndpoint:
    dbUser = User.get_user(user.sub)

    # Parse and validate request body
    body = SRE.CreateSREParams(**json.loads(lambda_event.body))
    
    # Default to first organization if org_id is not provided
    if body.org_id is None:
        body.org_id = dbUser.organizations[0]
    elif body.org_id not in dbUser.organizations:
        raise Exception("User does not have access to this organization", 403)

    # Validate that the user has access to the parameter definition
    ParameterDefinition.get_parameter_definition_for_user(body.pd_id, dbUser)

    # Create the SRE
    sre = SRE.create_sre(
        org_id=body.org_id,
        name=body.name,
        description=body.description,
        pd_id=body.pd_id,
        is_public=body.is_public,
    )

    return sre