from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import StructuredResponseEndpoint as SRE, User, SuccessResponse

def delete_sre_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse.SuccessResponse:
    sre_id = lambda_event.requestParameters.get("sre_id")
    if not sre_id:
        raise Exception("sre_id is required", 400)
    
    dbUser = User.get_user(user.sub)
    sre = SRE.get_sre_for_user(sre_id, dbUser)
    SRE.delete_sre(sre.sre_id)

    return SuccessResponse.SuccessResponse(**{
        "success": True
    })