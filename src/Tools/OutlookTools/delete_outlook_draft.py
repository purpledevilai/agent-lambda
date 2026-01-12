import json
from pydantic import Field, BaseModel
from LLM.AgentTool import AgentTool
from Services import OutlookService


class delete_outlook_draft(BaseModel):
    """
    Delete a draft email permanently without sending it.
    """
    integration_id: str = Field(description="The Outlook integration ID to use for authentication.")
    draft_id: str = Field(description="The draft ID to delete.")


def delete_outlook_draft_func(integration_id: str, draft_id: str) -> str:
    """
    Delete a draft permanently.
    
    Args:
        integration_id: The Outlook integration ID
        draft_id: The draft ID to delete
        
    Returns:
        JSON string confirming deletion
    """
    if not integration_id:
        raise Exception("integration_id is required.")
    if not draft_id:
        raise Exception("draft_id is required.")
    
    OutlookService.delete_draft(integration_id, draft_id)
    
    return json.dumps({
        "status": "deleted",
        "draft_id": draft_id,
    }, indent=2)


delete_outlook_draft_tool = AgentTool(params=delete_outlook_draft, function=delete_outlook_draft_func, pass_context=False)

