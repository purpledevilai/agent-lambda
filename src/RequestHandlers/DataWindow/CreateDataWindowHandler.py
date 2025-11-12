import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import DataWindow, User

def create_data_window_handler(lambda_event: LambdaEvent, user: CognitoUser) -> DataWindow.DataWindow:
    """
    Create a new DataWindow.
    
    POST /data-window
    Body: CreateDataWindowParams
    """
    db_user = User.get_user(user.sub)
    
    body = DataWindow.CreateDataWindowParams(**json.loads(lambda_event.body))
    
    # Default to user's first org if not specified
    if body.org_id == None:
        body.org_id = db_user.organizations[0]
    elif body.org_id not in db_user.organizations:
        raise Exception(f"User does not have access to this organization", 403)
    
    # Create the DataWindow
    data_window = DataWindow.create_data_window(
        org_id=body.org_id,
        data=body.data,
        name=body.name,
        description=body.description
    )
    
    return data_window

