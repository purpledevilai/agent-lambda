import json
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import DataWindow, User

def update_data_window_handler(lambda_event: LambdaEvent, user: CognitoUser) -> DataWindow.DataWindow:
    """
    Update a DataWindow.
    
    PUT /data-window/{data_window_id}
    Body: UpdateDataWindowParams
    """
    data_window_id = lambda_event.requestParameters.get("data_window_id")
    if not data_window_id:
        raise Exception("data_window_id is required in path", 400)
    
    body = DataWindow.UpdateDataWindowParams(**json.loads(lambda_event.body))
    
    # Get the DataWindow
    data_window = DataWindow.get_data_window(data_window_id)
    
    # Validate user has access to this org
    db_user = User.get_user(user.sub)
    if data_window.org_id not in db_user.organizations:
        raise Exception(f"DataWindow does not belong to user's organizations", 403)
    
    # Update fields if provided
    if body.name is not None:
        data_window.name = body.name
    if body.description is not None:
        data_window.description = body.description
    if body.data is not None:
        data_window.data = body.data
    
    # Save the updated DataWindow
    data_window = DataWindow.save_data_window(data_window)
    
    return data_window

