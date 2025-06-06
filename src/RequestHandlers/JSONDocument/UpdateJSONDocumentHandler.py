import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import JSONDocument, User

def update_json_document_handler(lambda_event: LambdaEvent, user: CognitoUser) -> JSONDocument.JSONDocument:
    # Parse request body
    body = JSONDocument.UpdateJSONDocumentParams(**json.loads(lambda_event.body))

    # Get document ID
    document_id = lambda_event.requestParameters.get("document_id")
    if not document_id:
        raise Exception("document_id is required", 400)

    # Get user
    db_user = User.get_user(user.sub)

    # Get the document
    json_document = JSONDocument.get_json_document_for_user(document_id, db_user)

    # Apply updates
    update_dict = {k: v for k, v in body.model_dump().items() if v is not None}
    json_document_dict = json_document.model_dump()
    json_document_dict.update(update_dict)
    updated_document = JSONDocument.JSONDocument(**json_document_dict)

    # Save and return
    JSONDocument.save_json_document(updated_document)

    return updated_document
