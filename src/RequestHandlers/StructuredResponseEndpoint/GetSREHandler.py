from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, StructuredResponseEndpoint as SRE


def get_sre_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SRE.StructuredResponseEndpoint:
    sre_id = lambda_event.requestParameters.get("sre_id")
    if not sre_id:
        raise Exception("sre_id is required", 400)

    dbUser = User.get_user(user.sub)
    return SRE.get_sre_for_user(sre_id, dbUser)