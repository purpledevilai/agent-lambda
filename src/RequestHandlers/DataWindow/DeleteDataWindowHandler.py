from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import DataWindow, User
from Models.SuccessResponse import SuccessResponse

def delete_data_window_handler(lambda_event: LambdaEvent, user: CognitoUser) -> SuccessResponse:
    """
    Delete a DataWindow.
    
    DELETE /data-window/{data_window_id}
    """
    data_window_id = lambda_event.requestParameters.get("data_window_id")
    if not data_window_id:
        raise Exception("data_window_id is required in path", 400)
    
    # Get the DataWindow
    data_window = DataWindow.get_data_window(data_window_id)
    
    # Validate user has access to this org
    db_user = User.get_user(user.sub)
    if data_window.org_id not in db_user.organizations:
        raise Exception(f"DataWindow does not belong to user's organizations", 403)
    
    # Delete the DataWindow
    DataWindow.delete_data_window(data_window_id)
    
    return SuccessResponse(success=True)

