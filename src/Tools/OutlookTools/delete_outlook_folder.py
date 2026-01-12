import json
from pydantic import Field, BaseModel
from LLM.AgentTool import AgentTool
from Services import OutlookService


class delete_outlook_folder(BaseModel):
    """
    Delete a custom mail folder. System folders (Inbox, Sent Items, Drafts, etc.) cannot be deleted.
    Any emails in the deleted folder will be permanently deleted.
    """
    integration_id: str = Field(description="The Outlook integration ID to use for authentication.")
    folder_id: str = Field(description="The folder ID to delete (from list_outlook_folders).")


def delete_outlook_folder_func(integration_id: str, folder_id: str) -> str:
    """
    Delete a mail folder.
    
    Args:
        integration_id: The Outlook integration ID
        folder_id: The folder ID to delete
        
    Returns:
        JSON string confirming deletion
    """
    if not integration_id:
        raise Exception("integration_id is required.")
    if not folder_id:
        raise Exception("folder_id is required.")
    
    OutlookService.delete_folder(integration_id, folder_id)
    
    return json.dumps({
        "status": "deleted",
        "folder_id": folder_id,
    }, indent=2)


delete_outlook_folder_tool = AgentTool(params=delete_outlook_folder, function=delete_outlook_folder_func, pass_context=False)

