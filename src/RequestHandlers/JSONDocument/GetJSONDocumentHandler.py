from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import User, JSONDocument
from typing import Optional

def get_json_document_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> JSONDocument.JSONDocument:
    # Get the path parameters
    document_id = lambda_event.requestParameters.get("document_id")
    if not document_id:
        raise Exception("document_id is required", 400)

    # If user is authenticated, get document for that user
    if user:
        db_user = User.get_user(user.sub)
        return JSONDocument.get_json_document_for_user(document_id, db_user)
    else:
        # No user provided, attempt to get public document
        return JSONDocument.get_public_json_document(document_id)
