from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
import json
from Models import JSONDocument, User

def create_json_document_handler(lambda_event: LambdaEvent, user: CognitoUser) -> JSONDocument:

    print("Creating JSON document handler")
    print(f"User: {user}")

    dbUser = User.get_user(user.sub)

    # Get the body of the request
    body = JSONDocument.CreateJSONDocumentParams(**json.loads(lambda_event.body))
    if (body.org_id == None):
        body.org_id = dbUser.organizations[0]
    elif (body.org_id not in dbUser.organizations):
        raise Exception("User does not have access to this organization", 403)
    
    # Create the json document
    parameter_definition = JSONDocument.create_json_document(body)

    return parameter_definition