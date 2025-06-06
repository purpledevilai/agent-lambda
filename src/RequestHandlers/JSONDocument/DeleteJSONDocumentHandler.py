from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import JSONDocument, User, SuccessResponse

def delete_json_document_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse.SuccessResponse:
    document_id = lambda_event.requestParameters.get("document_id")
    if not document_id:
        raise Exception("document_id is required", 400)

    db_user = User.get_user(user.sub)
    json_document = JSONDocument.get_json_document_for_user(document_id, db_user)
    JSONDocument.delete_json_document(json_document.document_id)

    return SuccessResponse.SuccessResponse(**{
        "success": True
    })
