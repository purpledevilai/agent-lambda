from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, SingleMessageEndpoint as SME


def get_sme_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SME.SingleMessageEndpoint:
    sme_id = lambda_event.requestParameters.get("sme_id")
    if not sme_id:
        raise Exception("sme_id is required", 400)

    dbUser = User.get_user(user.sub)
    return SME.get_sme_for_user(sme_id, dbUser)