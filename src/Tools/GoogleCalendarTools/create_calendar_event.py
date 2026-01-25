import json
from pydantic import Field, BaseModel
from typing import Optional, List
from LLM.AgentTool import AgentTool
from Services import GoogleCalendarService


class create_calendar_event(BaseModel):
    """
    Create a new event in Google Calendar. Supports both timed events and all-day events.
    
    Time format examples (RFC3339 for timed events):
    - With timezone offset: '2026-01-25T10:00:00-05:00' (Eastern Time)
    - With UTC: '2026-01-25T15:00:00Z'
    
    Date format for all-day events:
    - Simple date: '2026-01-25' (YYYY-MM-DD)
    
    Examples:
    - 1-hour meeting: start='2026-01-25T10:00:00Z', end='2026-01-25T11:00:00Z', all_day=False
    - All-day event: start='2026-01-25', end='2026-01-26', all_day=True (end date is exclusive)
    - Multi-day event: start='2026-01-25', end='2026-01-28', all_day=True (3 days)
    """
    integration_id: str = Field(description="The Google Calendar integration ID to use for authentication.")
    summary: str = Field(description="The title/summary of the event.")
    start_time: str = Field(
        description="Start time in RFC3339 format (e.g., '2026-01-25T10:00:00Z') or date for all-day events (e.g., '2026-01-25')."
    )
    end_time: str = Field(
        description="End time in RFC3339 format (e.g., '2026-01-25T11:00:00Z') or date for all-day events (e.g., '2026-01-26'). For all-day events, end date is exclusive."
    )
    calendar_id: Optional[str] = Field(
        default="primary",
        description="The calendar ID to create the event in. Use 'primary' for the user's main calendar."
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the event."
    )
    location: Optional[str] = Field(
        default=None,
        description="Location of the event (address or place name)."
    )
    attendees: Optional[List[str]] = Field(
        default=None,
        description="List of attendee email addresses to invite to the event."
    )
    timezone: Optional[str] = Field(
        default=None,
        description="Timezone for the event (e.g., 'America/New_York', 'Europe/London'). If not set, uses calendar's default timezone."
    )
    all_day: Optional[bool] = Field(
        default=False,
        description="Set to True for all-day events. When True, use date format (YYYY-MM-DD) for start_time and end_time."
    )


def create_calendar_event_func(
    integration_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    calendar_id: str = "primary",
    description: str = None,
    location: str = None,
    attendees: List[str] = None,
    timezone: str = None,
    all_day: bool = False
) -> str:
    """
    Create a new calendar event.
    
    Args:
        integration_id: The Google Calendar integration ID
        summary: Event title
        start_time: Start time (RFC3339 or date)
        end_time: End time (RFC3339 or date)
        calendar_id: The calendar ID (default "primary")
        description: Event description
        location: Event location
        attendees: List of attendee emails
        timezone: Event timezone
        all_day: Whether this is an all-day event
        
    Returns:
        JSON string with created event details
    """
    if not integration_id:
        raise Exception("integration_id is required.")
    if not summary:
        raise Exception("summary (event title) is required.")
    if not start_time:
        raise Exception("start_time is required.")
    if not end_time:
        raise Exception("end_time is required.")
    
    result = GoogleCalendarService.create_event(
        integration_id,
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        calendar_id=calendar_id,
        description=description,
        location=location,
        attendees=attendees,
        timezone=timezone,
        all_day=all_day
    )
    
    return json.dumps({
        "status": "created",
        "event_id": result.get("id"),
        "summary": result.get("summary"),
        "html_link": result.get("htmlLink"),
        "start": result.get("start"),
        "end": result.get("end"),
        "attendees_count": len(result.get("attendees", [])),
    }, indent=2)


create_calendar_event_tool = AgentTool(params=create_calendar_event, function=create_calendar_event_func, pass_context=False)

