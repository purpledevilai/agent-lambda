from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
from Models import DataWindow, User
from pydantic import BaseModel

class GetDataWindowsResponse(BaseModel):
    data_windows: list[DataWindow.DataWindow]

def get_data_windows_handler(lambda_event: LambdaEvent, user: CognitoUser) -> GetDataWindowsResponse:
    """
    Get all DataWindows for a specific organization.
    
    GET /data-windows?org_id={org_id}
    
    If org_id is not provided, defaults to user's first organization.
    """
    db_user = User.get_user(user.sub)
    
    # User must have at least one organization
    if len(db_user.organizations) == 0:
        raise Exception("User is not a member of any organizations", 400)
    
    # Get org_id from query params or default to first org
    org_id = None
    if lambda_event.queryStringParameters is not None:
        org_id = lambda_event.queryStringParameters.get("org_id")
    if org_id is None:
        org_id = db_user.organizations[0]
    elif org_id not in db_user.organizations:
        raise Exception("User is not a member of the specified organization", 403)
    
    # Get DataWindows for the specified org
    data_windows = DataWindow.get_data_windows_for_org(org_id)
    
    return GetDataWindowsResponse(data_windows=data_windows)

