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
    body = DataWindow.CreateDataWindowParams(**json.loads(lambda_event.body))
    
    # Get user and validate org membership
    db_user = User.get_user(user.sub)
    if body.org_id not in db_user.organizations:
        raise Exception(f"User does not belong to organization {body.org_id}", 403)
    
    # Create the DataWindow
    data_window = DataWindow.create_data_window(
        org_id=body.org_id,
        data=body.data,
        name=body.name,
        description=body.description
    )
    
    return data_window

