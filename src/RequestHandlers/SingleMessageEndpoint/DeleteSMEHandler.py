from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import SingleMessageEndpoint as SME, User, SuccessResponse

def delete_sme_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse.SuccessResponse:
    sme_id = lambda_event.requestParameters.get("sme_id")
    if not sme_id:
        raise Exception("sme_id is required", 400)
    
    dbUser = User.get_user(user.sub)
    sme = SME.get_sme_for_user(sme_id, dbUser)
    SME.delete_sme(sme.sme_id)

    return SuccessResponse.SuccessResponse(**{
        "success": True
    })